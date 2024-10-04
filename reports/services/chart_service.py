# 파이썬 표준 라이브러리
import os
import time
import logging
import io
import traceback
from datetime import datetime

# 서드파티 라이브러리
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

# 장고 관련 임포트
from django.conf import settings

# 로컬 애플리케이션 임포트
from ..services.openai_service import OpenAIService
from ..models import ChartReport, Price
from ..utils import get_current_price

logger = logging.getLogger(__name__)

class ChartCapture:
    def __init__(self):
        self.driver = None

    # 로컬 개발용
    # def create_driver(self):
    #     logger.info("ChromeDriver 설정 중...")
    #     try:
    #         chrome_options = Options()
    #         chrome_options.add_argument("--headless")
    #         chrome_options.add_argument("--start-maximized")
    #         chrome_options.add_argument("--no-sandbox")
    #         chrome_options.add_argument("--disable-dev-shm-usage")
    #         service = Service(ChromeDriverManager().install())
    #         self.driver = webdriver.Chrome(service=service, options=chrome_options)
    #         return self.driver
    #     except Exception as e:
    #         logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
    #         raise

    # EC2 서버용
    def create_driver(self):
        logger.info("ChromeDriver 설정 중...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 헤드리스 모드 사용
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080") 

            service = Service('/usr/local/bin/chromedriver')  # Specify the path to the ChromeDriver executable

            # Initialize the WebDriver with the specified options
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        
        except Exception as e:
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
            raise

    def capture_chart(self):
        try:
            self.driver = self.create_driver()
            self._navigate_to_chart()
            self._perform_chart_actions()
            image_url = self._capture_and_save_screenshot()
            self._save_current_price()
            return image_url
        except Exception as e:
            logger.error(f"차트 캡처 중 오류 발생: {e}\n{traceback.format_exc()}")
            return None
        finally:
            self._quit_driver()

    def _navigate_to_chart(self):
        self.driver.get("https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC")
        logger.info("페이지 로드 완료")
        time.sleep(10)

    def _click_element_by_xpath(self, xpath, element_name, wait_time=20):
        logger.debug(f"Trying to click on element: {element_name} with XPath: {xpath}")
        try:
            logger.debug(f"Waiting for element to be clickable...")
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            logger.debug(f"Element found: {element_name}")
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            logger.info(f"{element_name} 클릭 완료")
            WebDriverWait(self.driver, 2).until(
                EC.staleness_of(element)
            )
        except TimeoutException:
            logger.error(f"{element_name} 클릭을 기다리는 중 타임아웃 발생")
        except Exception as e:
            logger.error(f"{element_name} 클릭 중 오류 발생: {e}")
            raise

    def _click_indicator_option(self, indicator_xpath, indicator_name):
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

    def _perform_chart_actions(self):
        try:
            self._click_element_by_xpath(
                "//cq-menu[@class='ciq-menu ciq-period']",
                "시간 메뉴"
            )
            self._click_element_by_xpath(
                "//cq-item[./translate[text()='1시간']]",
                "1시간 옵션"
            )
            self._click_element_by_xpath(
                "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[2]/span",
                "차트설정"
            )
            dark_theme_xpath = "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[2]/cq-menu-dropdown/cq-themes/cq-themes-builtin/cq-item[2]"
            self._click_indicator_option(dark_theme_xpath, "다크테마")

            indicators = [
                ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[15]", "볼린저 밴드"),
                ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[81]", "RSI"),
                ("//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[53]", "MACD")
            ]

            for indicator_xpath, indicator_name in indicators:
                self._click_element_by_xpath(
                    "/html/body/div[1]/div[3]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]",
                    "지표 메뉴"
                )
                self._click_indicator_option(indicator_xpath, indicator_name)

        except Exception as e:
            logger.error(f"차트 액션 수행 중 오류 발생: {e}")
            raise

    # 로컬 개발용
    def _capture_and_save_screenshot(self):
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
        
    # #ec2 서버용
    # def _capture_and_save_screenshot(self):
    #     try:
    #         # 페이지가 완전히 로드될 때까지 대기
    #         WebDriverWait(self.driver, 20).until(
    #             EC.presence_of_element_located((By.XPATH, '//*[@id="fullChartiq"]/div/div'))
    #         )

    #         # 차트 요소 찾기
    #         chart_element = self.driver.find_element(By.XPATH, '//*[@id="fullChartiq"]/div/div')

    #         # 차트 요소의 크기 가져오기
    #         size = chart_element.size
            
    #         # 창 크기를 차트 크기에 맞게 조정 (높이에 여유를 두기 위해 100px 추가)
    #         self.driver.set_window_size(size['width'], size['height'] + 100)

    #         # 차트 요소의 위치 정보 가져오기
    #         location = chart_element.location

    #         # 전체 스크린샷 찍기
    #         png = self.driver.get_screenshot_as_png()

    #         # 이미지 처리
    #         im = Image.open(io.BytesIO(png))
    #         left = location['x']
    #         top = location['y']
    #         right = left + size['width']
    #         bottom = top + size['height']

    #         # 차트 부분만 크롭
    #         im = im.crop((left, top, right, bottom))

    #         # 이미지 저장
    #         current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    #         filename = f"chart_screenshot_{current_time}.png"
    #         save_dir = os.path.join(settings.MEDIA_ROOT, 'capture_chart')
    #         os.makedirs(save_dir, exist_ok=True)
    #         file_path = os.path.join(save_dir, filename)
    #         im.save(file_path)

    #         logger.info(f"스크린샷이 저장되었습니다: {file_path}")
    #         image_url = f"{settings.MEDIA_URL}capture_chart/{filename}"
    #         return image_url
    #     except Exception as e:
    #         logger.error(f"스크린샷 캡처 및 저장 중 오류 발생: {e}")
    #         return None

    def _save_current_price(self):
        current_price = get_current_price()
        if current_price:
            Price.objects.create(market="KRW-BTC", trade_price=current_price)
        logger.info(f"현재가 저장 완료: {current_price}")

    def _quit_driver(self):
        if self.driver:
            self.driver.quit()

class ChartService:
    def __init__(self):
        self.chart_capture = ChartCapture()
        self.openai_service = OpenAIService()

    def capture_and_analyze_chart(self):
        try:
            image_url = self.chart_capture.capture_chart()
            if not image_url:
                return {'error': '차트 캡처에 실패했습니다.'}

            file_path = os.path.join(settings.MEDIA_ROOT, image_url.replace(settings.MEDIA_URL, ""))
            analysis_result = self.openai_service.analyze_chart(file_path)

            if 'error' in analysis_result:
                return {'error': analysis_result['error']}

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

            return {
                'success': True,
                'message': '차트가 성공적으로 캡처 및 분석되었습니다.',
                'chart_report_id': chart_report.id,
                'image_url': image_url
            }

        except Exception as e:
            logger.error(f"차트 캡처 중 오류 발생: {e}\n{traceback.format_exc()}")
            return {'error': str(e)}