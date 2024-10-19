from django.db import models

class News(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    is_active = models.BooleanField(default=True)

class NewsItem(models.Model):
    feed = models.ForeignKey(News, on_delete=models.CASCADE, related_name='news_items')
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField()
    link = models.URLField()
    translated_title = models.CharField(max_length=200, blank=True)
    translated_content = models.TextField(blank=True)
    impact = models.CharField(max_length=50, blank=True)
    tickers = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True, null=True)
    ai_analysis = models.JSONField(null=True, blank=True)