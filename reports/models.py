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
    # MainReport 관계는 일시적으로 주석 처리
    # main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='chart_report')
    
    image_url = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    technical_analysis = models.JSONField()
    candlestick_analysis = models.JSONField()
    moving_average_analysis = models.JSONField()
    bollinger_bands_analysis = models.JSONField()
    rsi_analysis = models.JSONField()
    fibonacci_retracement_analysis = models.JSONField()
    macd_analysis = models.JSONField()
    support_resistance_analysis = models.JSONField()
    
    overall_recommendation = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Chart Report at {self.timestamp}"

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
