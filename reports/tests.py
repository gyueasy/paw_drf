import os
import sys
import django

# Django 설정 파일 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paw_drf.settings")
django.setup()

from django.test import TestCase
from reports.models import Price
from reports.utils import get_current_price

class PriceTestCase(TestCase):
    def test_get_and_save_current_price(self):
        # 현재가 가져오기
        current_price = get_current_price()
        self.assertIsNotNone(current_price)
        
        # 현재가 저장하기
        price = Price.objects.create(
            market="KRW-BTC",
            trade_price=current_price
        )
        
        # 저장된 가격 확인
        saved_price = Price.objects.first()
        self.assertEqual(saved_price.market, "KRW-BTC")
        self.assertEqual(saved_price.trade_price, current_price)

    def test_multiple_prices(self):
        # 여러 번 가격 저장하기
        for _ in range(5):
            current_price = get_current_price()
            Price.objects.create(
                market="KRW-BTC",
                trade_price=current_price
            )
        
        # 저장된 가격 개수 확인
        self.assertEqual(Price.objects.count(), 5)

    def test_invalid_market(self):
        # 잘못된 마켓 코드로 테스트
        invalid_price = get_current_price("INVALID-MARKET")
        self.assertIsNone(invalid_price)

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)