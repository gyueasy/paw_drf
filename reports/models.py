from django.db import models
from django.conf import settings


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
    created_at = models.DateTimeField(auto_now_add=True)
    news_analysis = models.TextField()

    def __str__(self):
        return f"News Report {self.id} created at {self.created_at}"

# 메인 리포트 모델
class MainReport(models.Model):
    title = models.CharField(max_length=200)
    recommendation = models.TextField()
    confidence_level = models.TextField()
    reasoning = models.TextField()
    overall_analysis = models.TextField()
    market_analysis = models.TextField()
    chart_analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Many-to-Many 관계 설정
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reports')

    @property
    def latest_weights(self):
        return self.weights.first()  # 가장 최근의 가중치 모델 반환
    
    @property
    def previous_reports(self):
        # 최근 10개의 이전 보고서 반환 (자신 제외)
        return MainReport.objects.filter(created_at__lt=self.created_at).order_by('-created_at')[:10]

    def __str__(self):
        return self.title
    
# 리포트 가중치 모델
class ReportWeights(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='weights')
    overall_weight = models.FloatField(default=1.0)
    fear_greed_index_weight = models.FloatField(default=1.0)
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
    reason = models.TextField(blank=True, null=True)
    accuracy = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Weights for {self.main_report.title} at {self.created_at}"

class Price(models.Model):
    market = models.CharField(max_length=20)  # 예: "KRW-BTC"
    timestamp = models.DateTimeField(auto_now_add=True)
    trade_price = models.DecimalField(max_digits=20, decimal_places=8)
    
    def __str__(self):
        return f"{self.market}: {self.trade_price} at {self.timestamp}"

class Accuracy(models.Model):
    main_report = models.ForeignKey(MainReport, on_delete=models.CASCADE, related_name='accuracies')
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='accuracies')
    accuracy = models.FloatField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Accuracy: {self.accuracy} for report {self.main_report.id} at {self.calculated_at}"