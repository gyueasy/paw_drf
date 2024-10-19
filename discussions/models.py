from django.db import models
from django.conf import settings

class Discussion(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True)

class AIComment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='ai_comments')
    role = models.CharField(max_length=50)  # 트레이더의 이름을 저장
    strategy = models.CharField(max_length=100)  # 트레이더의 전략 설명을 저장
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)