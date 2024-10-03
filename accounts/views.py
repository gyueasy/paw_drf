from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from .serializers import AccountSerializer, ProfileSerializer, CommentSerializer
from reports.models import MainReport
from .models import Comment
from .permissions import IsOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class GoogleLoginView(SocialLoginView):
    """
    Google OAuth2 로그인 프로세스와 토큰 생성을 처리합니다.
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        user = self.user

        # RefreshToken 생성
        refresh = RefreshToken.for_user(user)

        # 응답에 refresh 토큰과 access 토큰 추가
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)

        logger.info(f"Google 로그인: 사용자 {user.email}가 성공적으로 로그인했습니다.")
        return response

class CustomLogoutView(LogoutView):
    """
    사용자 로그아웃 및 토큰 무효화를 처리합니다.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # 사용자의 모든 액세스 토큰 무효화
        OutstandingToken.objects.filter(user=user).update(blacklisted=True)

        logger.info(f"사용자 {user.email}가 성공적으로 로그아웃했습니다.")
        return Response({"detail": "로그아웃이 성공적으로 완료되었습니다."}, status=status.HTTP_200_OK)

class AccountView(APIView):
    """
    계정 업데이트 및 삭제 작업을 처리합니다.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = AccountSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"사용자 {request.user.email}의 계정이 업데이트되었습니다.")
            return Response({"detail": "계정이 성공적으로 업데이트되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        email = user.email
        user.delete()
        logger.info(f"사용자 {email}의 계정이 삭제되었습니다.")
        return Response({"detail": "계정이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

class ProfileView(APIView):
    """
    사용자 프로필 정보를 검색합니다.
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # 15분 동안 캐시
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentView(APIView):
    """
    댓글에 대한 CRUD 작업을 처리합니다.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, report_id):
        report = get_object_or_404(MainReport, id=report_id)
        comments = report.comments.select_related('user').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, report_id):
        report = get_object_or_404(MainReport, id=report_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, report=report)
            logger.info(f"사용자 {request.user.email}가 리포트 {report_id}에 댓글을 작성했습니다.")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"댓글 작성 실패: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"사용자 {request.user.email}가 댓글 {comment_id}를 업데이트했습니다.")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(request, comment)
        comment.delete()
        logger.info(f"사용자 {request.user.email}가 댓글 {comment_id}를 삭제했습니다.")
        return Response(status=status.HTTP_204_NO_CONTENT)

class LikeView(APIView):
    """
    리포트 좋아요 및 좋아요 취소를 처리합니다.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        report = get_object_or_404(MainReport, id=report_id)
        is_liked = report.likers.filter(id=request.user.id).exists()
        return Response({"status": "liked" if is_liked else "not liked"}, status=status.HTTP_200_OK)

    def post(self, request, report_id):
        report = get_object_or_404(MainReport, id=report_id)
        if not report.likers.filter(id=request.user.id).exists():
            report.likers.add(request.user)
            logger.info(f"사용자 {request.user.email}가 리포트 {report_id}에 좋아요를 눌렀습니다.")
            return Response({"status": "liked"}, status=status.HTTP_200_OK)
        return Response({"status": "already liked"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, report_id):
        report = get_object_or_404(MainReport, id=report_id)
        if report.likers.filter(id=request.user.id).exists():
            report.likers.remove(request.user)
            logger.info(f"사용자 {request.user.email}가 리포트 {report_id}의 좋아요를 취소했습니다.")
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)
        return Response({"status": "not liked"}, status=status.HTTP_400_BAD_REQUEST)