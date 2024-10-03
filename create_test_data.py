import os
import django
import random
from datetime import timedelta

# Django 설정 파일 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paw_drf.settings")
django.setup()

from django.utils import timezone
from reports.models import MainReport, Price, Accuracy, ReportWeights

def create_test_data():
    # MainReport 생성
    main_report = MainReport.objects.create(
        title="Test Report",
        recommendation="BUY, 70%",
        confidence_level="High",
        reasoning="This is a test reasoning",
        overall_analysis="This is a test overall analysis",
        market_analysis="This is a test market analysis",
        chart_analysis="This is a test chart analysis",
        created_at=timezone.now()
    )
    print(f"Created MainReport: {main_report}")

    # Price 데이터 생성
    current_price = 50000  # 시작 가격
    for i in range(10):  # 10개의 가격 데이터 생성
        price = Price.objects.create(
            market="KRW-BTC",
            timestamp=timezone.now() - timedelta(hours=i),
            trade_price=current_price
        )
        print(f"Created Price: {price}")
        current_price += random.randint(-1000, 1000)  # 가격 변동

    # Accuracy 데이터 생성
    for i in range(7):  # 7일치 Accuracy 데이터 생성
        accuracy = Accuracy.objects.create(
            main_report=main_report,
            price=Price.objects.latest('timestamp'),
            accuracy=random.uniform(0, 1),
            calculated_at=timezone.now() - timedelta(days=i)
        )
        print(f"Created Accuracy: {accuracy}")

    # ReportWeights 생성
    weights = ReportWeights.objects.create(
        main_report=main_report,
        overall_weight=1.0,
        fear_greed_index_weight=1.0,
        news_weight=1.0,
        chart_overall_weight=1.0,
        chart_technical_weight=1.0,
        chart_candlestick_weight=1.0,
        chart_moving_average_weight=1.0,
        chart_bollinger_bands_weight=1.0,
        chart_rsi_weight=1.0,
        chart_fibonacci_weight=1.0,
        chart_macd_weight=1.0,
        chart_support_resistance_weight=1.0
    )
    print(f"Created ReportWeights: {weights}")

if __name__ == "__main__":
    create_test_data()