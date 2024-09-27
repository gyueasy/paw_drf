from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=150, unique=True)
    username = models.CharField(max_length=150)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
    likes = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'username']

    def __str__(self):
        return self.email