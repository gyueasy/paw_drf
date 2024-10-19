from django.db import models

class News(models.Model):
    name = models.CharField(max_length=500)
    url = models.TextField(unique=True)
    is_active = models.BooleanField(default=True)

class NewsItem(models.Model):
    feed = models.ForeignKey(News, on_delete=models.CASCADE, related_name='news_items')
    title = models.CharField(max_length=500)
    content = models.TextField()
    published_date = models.DateTimeField()
    link = models.TextField()
    translated_title = models.CharField(max_length=500, blank=True)
    translated_content = models.TextField(blank=True)
    impact = models.CharField(max_length=50, blank=True)
    tickers = models.CharField(max_length=100, blank=True)
    image_url = models.TextField(blank=True, null=True)
    ai_analysis = models.JSONField(null=True, blank=True)
