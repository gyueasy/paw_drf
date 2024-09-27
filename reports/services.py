from selenium.webdriver.common.by import By
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.conf import settings
import base64
from openai import OpenAI
import time
import json

class ChartService:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=chrome_options)

    def take_screenshot(self, url, filename):
        self.driver.get(url)
        time.sleep(15)  # Upbit 차트가 완전히 로드될 때까지 대기

        # capture_chart 디렉토리 경로 생성
        capture_dir = os.path.join(settings.MEDIA_ROOT, 'capture_chart')
        
        # capture_chart 디렉토리가 없으면 생성
        if not os.path.exists(capture_dir):
            os.makedirs(capture_dir)

        screenshot_path = os.path.join(capture_dir, filename)
        
        # 전체 페이지의 스크린샷을 찍습니다.
        self.driver.save_screenshot(screenshot_path)
        
        return screenshot_path

    def __del__(self):
        self.driver.quit()

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_chart(self, image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Bitcoin analyst with deep knowledge of technical analysis and chart patterns. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze the current Bitcoin chart using the following technical indicators and provide your insights:
    1. Technical Analysis
    2. Candlestick Patterns
    3. Moving Averages
    4. Bollinger Bands
    5. Relative Strength Index (RSI)
    6. Fibonacci Retracement
    7. MACD (Moving Average Convergence Divergence)
    8. Support and Resistance Levels

    For each indicator, provide a brief analysis and a clear recommendation: Buy, Sell, or Hold.
    Your response MUST be ONLY in the following JSON format, with no additional text before or after:

    {
    "Technical Analysis": {"analysis": "", "recommendation": ""},
    "Candlestick Patterns": {"analysis": "", "recommendation": ""},
    "Moving Averages": {"analysis": "", "recommendation": ""},
    "Bollinger Bands": {"analysis": "", "recommendation": ""},
    "RSI": {"analysis": "", "recommendation": ""},
    "Fibonacci Retracement": {"analysis": "", "recommendation": ""},
    "MACD": {"analysis": "", "recommendation": ""},
    "Support and Resistance Levels": {"analysis": "", "recommendation": ""},
    "Overall Recommendation": ""
    }"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            print(f"Raw API response: {content}")  # 디버깅을 위해 원본 응답 출력
            
            # JSON 시작 부분을 찾아 그 이후의 내용만 파싱
            json_start = content.find('{')
            if json_start != -1:
                content = content[json_start:]
            
            # JSON 끝 부분을 찾아 그 이전의 내용만 파싱
            json_end = content.rfind('}')
            if json_end != -1:
                content = content[:json_end+1]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            print(f"Problematic content: {content}")
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            print(f"Error in analyze_chart: {str(e)}")
            return {"error": f"Error analyzing chart: {str(e)}"}