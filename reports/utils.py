import requests
import logging
from decimal import Decimal
from datetime import datetime

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

def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    params = {
        "limit": 1,  # 최신 데이터 1개만 가져옵니다.
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
        
        data = response.json()
        
        if data["metadata"]["error"]:
            raise Exception(f"API 오류: {data['metadata']['error']}")
        
        fng_data = data["data"][0]
        
        # Unix timestamp를 datetime 객체로 변환
        timestamp = datetime.fromtimestamp(int(fng_data["timestamp"]))
        
        return {
            "value": int(fng_data["value"]),
            "value_classification": fng_data["value_classification"],
            "timestamp": timestamp,
            "time_until_update": int(fng_data["time_until_update"]) if "time_until_update" in fng_data else None
        }
    
    except requests.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"API 응답 파싱 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return None