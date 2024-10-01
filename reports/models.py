from django.db import models
from django.conf import settings
from django.utils import timezone

# 메인 리포트 모델
class MainReport(models.Model):
    title = models.TextField(max_length=200)
    recommendation = models.TextField(max_length=50)
    confidence_level = models.TextField(null=True, blank=True)
    reasoning = models.TextField()
    overall_analysis = models.TextField()
    market_analysis = models.TextField()
    chart_analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chart_report_id = models.IntegerField(null=True, blank=True)
    news_report_id = models.IntegerField(null=True, blank=True)
    weights_id = models.IntegerField(null=True, blank=True)
    likers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_reports', blank=True)

    def __str__(self):
        return self.title

# 차트 리포트 모델
class ChartReport(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='chart_report', null=True)
    image_url = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    technical_analysis = models.JSONField()
    candlestick_analysis = models.JSONField()
    moving_average_analysis = models.JSONField()
    bollinger_bands_analysis = models.JSONField()
    rsi_analysis = models.JSONField()
    fibonacci_retracement_analysis = models.JSONField()
    macd_analysis = models.JSONField()
    support_resistance_analysis = models.JSONField()
    overall_recommendation = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Chart Report for {self.main_report.title if self.main_report else 'Unassigned'}"


# 뉴스 리포트 모델
class NewsReport(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='news_report', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    news_analysis = models.JSONField()

    def __str__(self):
        return f"News Report for {self.main_report.title if self.main_report else 'Unassigned'}"


    
# 리포트 가중치 모델
class ReportWeights(models.Model):
    main_report = models.OneToOneField(MainReport, on_delete=models.CASCADE, related_name='weights', null=True)
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
    reasoning = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'overall_weight': self.overall_weight,
            'fear_greed_index_weight': self.fear_greed_index_weight,
            'news_weight': self.news_weight,
            'chart_overall_weight': self.chart_overall_weight,
            'chart_technical_weight': self.chart_technical_weight,
            'chart_candlestick_weight': self.chart_candlestick_weight,
            'chart_moving_average_weight': self.chart_moving_average_weight,
            'chart_bollinger_bands_weight': self.chart_bollinger_bands_weight,
            'chart_rsi_weight': self.chart_rsi_weight,
            'chart_fibonacci_weight': self.chart_fibonacci_weight,
            'chart_macd_weight': self.chart_macd_weight,
            'chart_support_resistance_weight': self.chart_support_resistance_weight,
            'reasoning': self.reasoning,
        }

    def __str__(self):
        return f"Weights for {self.main_report.title if self.main_report else 'Unassigned'}"

class Price(models.Model):
    main_report = models.ForeignKey(MainReport, on_delete=models.CASCADE, related_name='prices', null=True)
    market = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    trade_price = models.DecimalField(max_digits=20, decimal_places=8)
    
    def __str__(self):
        return f"{self.market}: {self.trade_price} at {self.timestamp}"


class Accuracy(models.Model):
    RECOMMENDATION_CHOICES = [
        ('BUY', 1),
        ('SELL', -1),
        ('HOLD', 0),
    ]

    accuracy = models.FloatField(default=0)
    average_accuracy = models.FloatField(default=0)
    calculated_at = models.DateTimeField(default=timezone.now)
    recommendation = models.CharField(max_length=4, choices=[(r, r) for r, _ in RECOMMENDATION_CHOICES])
    recommendation_value = models.IntegerField(default=0)
    price_change = models.FloatField(default=0)
    is_correct = models.BooleanField(default=False)

    @staticmethod
    def calculate_and_save_accuracy():
        from .models import MainReport, Price  # 순환 임포트 방지를 위해 여기서 임포트

        latest_report = MainReport.objects.order_by('-created_at').first()
        latest_price = Price.objects.order_by('-timestamp').first()
        previous_price = Price.objects.order_by('-timestamp')[1:2].first()

        if not latest_report or not latest_price or not previous_price:
            accuracy = 1.0
            recommendation = 'HOLD'
            recommendation_value = 0
            price_change = 0
            is_correct = False
        else:
            recommendation = latest_report.recommendation.split(',')[0].strip().upper()
            recommendation_value = dict(Accuracy.RECOMMENDATION_CHOICES)[recommendation]
            
            price_change = ((latest_price.trade_price - previous_price.trade_price) / previous_price.trade_price) * 100

            if recommendation == "BUY" and price_change > 0:
                accuracy = 1.0
                is_correct = True
            elif recommendation == "SELL" and price_change < 0:
                accuracy = 1.0
                is_correct = True
            elif recommendation == "HOLD" and -0.5 <= price_change <= 0.5:
                accuracy = 1.0
                is_correct = True
            else:
                accuracy = 0.0
                is_correct = False

        # 새 Accuracy 객체 생성 및 저장
        new_accuracy = Accuracy(
            accuracy=accuracy,
            recommendation=recommendation,
            recommendation_value=recommendation_value,
            price_change=price_change,
            is_correct=is_correct
        )
        new_accuracy.save()

        # 평균 정확도 계산 및 저장 (퍼센트로 변환)
        all_accuracies = Accuracy.objects.all()
        average_accuracy = (sum(acc.accuracy for acc in all_accuracies) / all_accuracies.count()) * 100
        new_accuracy.average_accuracy = average_accuracy
        new_accuracy.save()

        return new_accuracy

    def __str__(self):
        return f"Accuracy: {self.accuracy:.2f}, Avg: {self.average_accuracy:.2f}%, Recommendation: {self.recommendation} ({self.recommendation_value}), Price Change: {self.price_change:.2f}%, Correct: {self.is_correct}, Calculated at: {self.calculated_at}"