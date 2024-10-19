from rest_framework import serializers
from .models import Discussion, AIComment

class AICommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIComment
        fields = ['id', 'role', 'strategy', 'content', 'created_at']

class DiscussionSerializer(serializers.ModelSerializer):
    ai_comments = AICommentSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Discussion
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'image_url', 'ai_comments']