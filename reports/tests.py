from django.test import TestCase
from .models import MainReport, Price, Accuracy

class ReportModelTests(TestCase):

    def setUp(self):
        # 테스트 데이터 삽입
        self.main_report = MainReport.objects.create(
            recommendation="Hold, 70",
            # 기타 필드도 필요한 경우 추가
        )

        self.price_current = Price.objects.create(
            market="KRW-BTC",
            trade_price=86408000.00000000
        )

        self.price_previous = Price.objects.create(
            market="KRW-BTC",
            trade_price=86603000.00000000
        )

        self.accuracy = Accuracy.objects.create(
            main_report=self.main_report,
            price=self.price_current,
            accuracy=1.0  # 적중률 설정 (예시)
        )

    def test_accuracy_creation(self):
        # Accuracy 인스턴스가 잘 생성되었는지 확인
        self.assertEqual(self.accuracy.main_report, self.main_report)
        self.assertEqual(self.accuracy.price, self.price_current)
        self.assertEqual(self.accuracy.accuracy, 1.0)

    def test_price_creation(self):
        # Price 인스턴스가 잘 생성되었는지 확인
        self.assertEqual(self.price_current.trade_price, 86408000.00000000)
        self.assertEqual(self.price_previous.trade_price, 86603000.00000000)

    def test_main_report_recommendation(self):
        # MainReport의 추천을 확인
        self.assertEqual(self.main_report.recommendation, "Hold, 70")
