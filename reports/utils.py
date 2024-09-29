import requests

def get_current_price(market="KRW-BTC"):
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": market}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["trade_price"]
    return None