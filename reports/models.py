from django.db import models
from django.conf import settings

# 메인 리포트 모델
class MainReport(models.Model):
    title = models.CharField(max_length=200)
    overall_analysis = models.TextField()
    market_analysis = models.TextField()
    chart_analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Many-to-Many 관계 설정
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reports')

    def __str__(self):
        return self.title

# 차트 리포트 모델
class ChartReport(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='chart_report')
    technical_analysis = models.TextField()
    candlestick_analysis = models.TextField()
    moving_average_analysis = models.TextField()
    bollinger_bands_analysis = models.TextField()
    rsi_analysis = models.TextField()
    fibonacci_retracement_analysis = models.TextField()
    macd_analysis = models.TextField()
    support_resistance_analysis = models.TextField()
    chart_image = models.ImageField(upload_to='chart_images/')
    chart_data = models.JSONField()

    def __str__(self):
        return f"Chart Report for {self.main_report.title}"

# 뉴스 리포트 모델
class NewsReport(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='news_report')
    news_analysis = models.TextField()

    def __str__(self):
        return f"News Report for {self.main_report.title}"

# 리포트 가중치 모델
class ReportWeights(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='weights')
    overall_weight = models.FloatField(default=1.0)
    market_weight = models.FloatField(default=1.0)
    news_weight = models.FloatField(default=1.0)
    chart_overall_weight = models.FloatField(default=1.0)
    chart_technical_weight = models.FloatField(default=1.0)
    chart_candlestick_weight = models.FloatField(default=1.0)
    chart_moving_average_weight = models.FloatField(default=1.0)
    chart_bollinger_bands_weight = models.FloatField(default=1.0)
    chart_rsi_weight = models.FloatField(default=1.0)
    chart_fibonacci_weight = models.FloatField(default=1.0)
    chart_macd_weight = models.FloatField(default=1.0)
    chart_support_resistance_weight = models.FloatField(default=1.0)

    def __str__(self):
        return f"Weights for {self.main_report.title}"
