from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=False):
        user = super().save_user(request, user, form, commit=False)
        # 여기에 추가 필드 설정
        user.nickname = form.cleaned_data.get('nickname', '')
        user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        # 소셜 계정에서 정보 가져오기
        social_data = sociallogin.account.extra_data

        user.nickname = social_data.get('name', '')
        user.save()
        return user