from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.views import LogoutView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response
from .models import User, Comment
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .serializers import AccountSerializer, ProfileSerializer, CommentSerializer
from reports.models import MainReport

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        user = self.user

        # 사용자 확인
        print(f"GoogleLogin 호출: 사용자 - {user}")

        # RefreshToken 생성
        refresh = RefreshToken.for_user(user)

        # 응답에 refresh token과 access token 추가
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)

        print(f"Access Token: {response.data['access']}")
        print(f"Refresh Token: {response.data['refresh']}")

        return response

class CustomLogoutView(LogoutView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request, *args, **kwargs):
        print(f"로그아웃 요청: {request.user}")  # 디버깅 라인
        user = request.user

        # 현재 사용자의 모든 액세스 토큰을 조회
        tokens = OutstandingToken.objects.filter(user=user)

        # 각 토큰을 블랙리스트에 추가하여 무효화
        for token in tokens:
            BlacklistedToken.objects.create(token=token)

        # 기본 로그아웃 동작 수행
        return Response({"detail": "로그아웃이 완료되었습니다."}, status=status.HTTP_200_OK)

class AccountView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        print(f"요청한 사용자: {user}")
        if user.is_anonymous:
            return Response({"detail": "사용자가 인증되지 않았습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = AccountSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "계정이 성공적으로 업데이트되었습니다."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"detail": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, report_id):
        report = MainReport.objects.get(id=report_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, report=report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id, user=request.user)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id, user=request.user)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)