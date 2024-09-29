from rest_framework import serializers
from .models import User
from .validators import validate_nickname

class AccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    nickname = serializers.CharField(validators=[validate_nickname])

    class Meta:
        model = User
        fields = ['id', 'nickname', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'email']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField(validators=[validate_nickname])

    class Meta:
        model = User
        fields = ['email', 'nickname', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password']
        )
        return user