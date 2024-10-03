import requests
import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from .models import MainReport, Price, Accuracy
from django.db import models

logger = logging.getLogger(__name__)

def get_current_price(market="KRW-BTC"):
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": market}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["trade_price"]
    return None

def calculate_price_change(current_price, previous_price):
    current_price = Decimal(str(current_price))
    previous_price = Decimal(str(previous_price))
    return ((current_price - previous_price) / previous_price) * 100
