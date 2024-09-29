# Python standard library imports
import io
import json
import logging
import os
import time
from datetime import datetime

# Django imports
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Third-party imports
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    WebDriverException,
    NoSuchElementException
)
from webdriver_manager.chrome import ChromeDriverManager

# Local application imports
from .models import ChartReport, NewsReport
from .services import OpenAIService, NewsService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartCapture:
    def __init__(self):
        self.driver = None

    def create_driver(self):
        logger.info("ChromeDriver 설정 중...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        except Exception as e:
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
            raise

    def click_element_by_xpath(self, xpath, element_name, wait_time=30):
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            element.click()
            logger.info(f"{element_name} 클릭 완료")
            time.sleep(2)
        except Exception as e:
            logger.error(f"{element_name} 클릭 중 오류 발생: {e}")
            raise

    def click_indicator_option(self, indicator_xpath, indicator_name):
        try:
            indicator_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, indicator_xpath))
            )
            if not indicator_element.is_displayed():
                actions = ActionChains(self.driver)
                actions.move_to_element(indicator_element).perform()
            indicator_element.click()
            logger.info(f"{indicator_name} 옵션 클릭 완료")
            time.sleep(1)
        except TimeoutException:
            logger.error(f"{indicator_name} 옵션을 찾을 수 없습니다.")
        except Exception as e:
            logger.error(f"{indicator_name} 옵션 클릭 중 오류 발생: {e}")

    def perform_chart_actions(self):
        self.click_element_by_xpath(
            "//cq-menu[@class='ciq-menu ciq-period']",
            "시간 메뉴"
        )
        self.click_element_by_xpath(
            "//cq-item[./translate[text()='1시간']]",
            "1시간 옵션"
        )
        self.click_element_by_xpath(
            "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[2]/span",
            "차트설정"
        )
        dark_theme_xpath = "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[2]/cq-menu-dropdown/cq-themes/cq-themes-builtin/cq-item[2]"
        self.click_indicator_option(dark_theme_xpath, "다크테마")

        indicators = [
            ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[15]", "볼린저 밴드"),
            ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[81]", "RSI"),
            ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[53]", "MACD")
        ]

        for indicator_xpath, indicator_name in indicators:
            self.click_element_by_xpath(
                "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]",
                "지표 메뉴"
            )
            self.click_indicator_option(indicator_xpath, indicator_name)

    def capture_and_encode_screenshot(self):
        try:
            png = self.driver.get_screenshot_as_png()
            img = Image.open(io.BytesIO(png))
            img.thumbnail((2000, 2000))
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_screenshot_{current_time}.png"
            save_dir = os.path.join(settings.MEDIA_ROOT, 'capture_chart')
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, filename)
            img.save(file_path)
            logger.info(f"스크린샷이 저장되었습니다: {file_path}")
            image_url = f"{settings.MEDIA_URL}capture_chart/{filename}"
            return image_url
        except Exception as e:
            logger.error(f"스크린샷 캡처 및 저장 중 오류 발생: {e}")
            return None

    def capture_chart(self):
        try:
            self.create_driver()
            self.driver.get("https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC")
            logger.info("페이지 로드 완료")
            time.sleep(10)
            logger.info("차트 작업 시작")
            self.perform_chart_actions()
            logger.info("차트 작업 완료")
            image_url = self.capture_and_encode_screenshot()
            if image_url:
                logger.info(f"스크린샷 캡처 완료. 이미지 URL: {image_url}")
                return image_url
            else:
                logger.error("스크린샷 캡처 실패")
                return None
        except WebDriverException as e:
            logger.error(f"WebDriver 오류 발생: {e}")
            return None
        except Exception as e:
            logger.error(f"차트 캡처 중 오류 발생: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

@csrf_exempt
def capture_and_analyze_chart(request):
    if request.method == 'POST':
        try:
            # 차트 캡처
            chart_capture = ChartCapture()
            image_url = chart_capture.capture_chart()
            file_path = os.path.join(settings.MEDIA_ROOT, image_url.replace(settings.MEDIA_URL, ""))  # 실제 파일 경로
            
            if not image_url:
                return JsonResponse({'error': '차트 캡처에 실패했습니다.'}, status=500)

            # OpenAI를 사용한 차트 분석
            openai_service = OpenAIService()
            analysis_result = openai_service.analyze_chart(file_path)  # file_path를 전달

            if 'error' in analysis_result:
                return JsonResponse({'error': analysis_result['error']}, status=500)

            # ChartReport 모델에 결과 저장
            chart_report = ChartReport(
                image_url=image_url,
                technical_analysis=analysis_result['Technical Analysis'],
                candlestick_analysis=analysis_result['Candlestick Patterns'],
                moving_average_analysis=analysis_result['Moving Averages'],
                bollinger_bands_analysis=analysis_result['Bollinger Bands'],
                rsi_analysis=analysis_result['RSI'],
                fibonacci_retracement_analysis=analysis_result['Fibonacci Retracement'],
                macd_analysis=analysis_result['MACD'],
                support_resistance_analysis=analysis_result['Support and Resistance Levels'],
                overall_recommendation=analysis_result['Overall Recommendation']
            )
            chart_report.save()

            return JsonResponse({
                'success': True,
                'message': '차트가 성공적으로 캡처 및 분석되었습니다.',
                'chart_report_id': chart_report.id,
                'image_url': image_url
            })

        except Exception as e:
            logger.error(f"차트 캡처 및 분석 중 오류 발생: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)


@csrf_exempt
def crawl_and_analyze_news(request):
    if request.method == 'POST':
        try:
            news_service = NewsService()
            news_items = news_service.crawl_news()
            
            openai_service = OpenAIService()
            analysis_result = openai_service.analyze_news(news_items)
            
            if "error" in analysis_result:
                logger.error(f"Analysis error: {analysis_result['error']}")
                return JsonResponse({'error': analysis_result["error"]}, status=500)
            
            news_report = NewsReport(
                news_analysis=json.dumps(analysis_result)
            )
            news_report.save()
            
            return JsonResponse({
                'success': True,
                'message': '뉴스가 성공적으로 크롤링, 분석 및 저장되었습니다.',
                'news_report_id': news_report.id,
                'created_at': news_report.created_at.isoformat(),
                'analysis_summary': {
                    'market_sentiment': analysis_result.get('market_sentiment', ''),
                    'key_events_count': len(analysis_result.get('key_events', [])),
                    'potential_impact': analysis_result.get('potential_impact', ''),
                    'notable_trends_count': len(analysis_result.get('notable_trends', []))
                }
            })

        except Exception as e:
            logger.error(f"뉴스 크롤링 및 분석 중 오류 발생: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)