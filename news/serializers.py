
from rest_framework import serializers
from .models import NewsItem

class NewsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsItem
        fields = ['id', 'feed', 'title', 'content', 'published_date', 'link',
                'translated_title', 'translated_content', 'impact', 'tickers',
                'image_url', 'ai_analysis']