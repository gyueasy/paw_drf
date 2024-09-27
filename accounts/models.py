from django.db import models
from django.contrib.auth.models import AbstractUser

# 사용자 모델
class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=150, unique=True)
    username = models.CharField(max_length=150)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)   # 사용자가 받은 총 좋아요 수

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'username']

    def __str__(self):
        return self.email

# 코멘트 모델
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    report = models.ForeignKey('reports.MainReport', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.nickname} on {self.report.title}"