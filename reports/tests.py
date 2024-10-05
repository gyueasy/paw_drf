from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import os
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ChartCaptureTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = cls.create_driver()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()
        super().tearDownClass()

    @staticmethod
    def create_driver():
        logger.info("ChromeDriver 설정 중...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            service = Service(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
            raise

    @staticmethod
    def wait_and_click(driver, by, value, element_name, wait_time=30):
        try:
            element = WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((by, value))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(2)  # 스크롤 후 잠시 대기
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            logger.info(f"{element_name} 클릭 완료")
            time.sleep(2)  # 클릭 후 잠시 대기
        except TimeoutException:
            logger.error(f"{element_name} 요소를 찾는 데 시간이 초과되었습니다.")
            driver.save_screenshot(f"error_{element_name}.png")
            raise
        except ElementClickInterceptedException:
            logger.error(f"{element_name} 요소를 클릭할 수 없습니다. 다른 요소에 가려져 있을 수 있습니다.")
            driver.save_screenshot(f"error_{element_name}.png")
            raise
        except NoSuchElementException:
            logger.error(f"{element_name} 요소를 찾을 수 없습니다.")
            driver.save_screenshot(f"error_{element_name}.png")
            raise
        except Exception as e:
            logger.error(f"{element_name} 클릭 중 오류 발생: {e}")
            driver.save_screenshot(f"error_{element_name}.png")
            raise
        
    def perform_chart_actions(self):
        try:
            # 페이지가 완전히 로드될 때까지 대기
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 시간 메뉴 클릭
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[1]",
                "시간 메뉴"
            )
            
            # 1시간 옵션 선택
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[1]/cq-menu-dropdown/cq-item[8]",
                "1시간 옵션"
            )

            # 차트 설정 메뉴 클릭
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[2]",
                "차트 설정"
            )
            # 다크모드 옵션 선택
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[2]/cq-menu-dropdown/cq-themes/cq-themes-builtin/cq-item[2]",
                "Dark Theme"
            )
            
            # 지표 메뉴 클릭
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]",
                "지표 메뉴"
            )
            
            # 볼린저 밴드 옵션 선택
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[15]",
                "볼린저 밴드 옵션"
            )

            # 지표 메뉴 클릭
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]",
                "지표 메뉴"
            )
            
            # RSI 옵션 선택
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[81]",
                "RSI 옵션"
            )

            # 지표 메뉴 클릭
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]",
                "지표 메뉴"
            )
            
            # MACD 옵션 선택
            self.wait_and_click(
                self.driver,
                By.XPATH,
                "/html/body/div[1]/div[2]/div[3]/span/div/div/div[1]/div/div/cq-menu[3]/cq-menu-dropdown/cq-scroll/cq-studies/cq-studies-content/cq-item[53]",
                "MACD 옵션"
            )

        except Exception as e:
            logger.error(f"차트 조작 중 오류 발생: {e}")
            self.driver.save_screenshot("error_chart_manipulation.png")
            raise

    def capture_and_encode_screenshot(self):
        try:
            logger.info("스크린샷 캡처 시작...")
            # 스크린샷 캡처
            png = self.driver.get_screenshot_as_png()
            logger.info("스크린샷 캡처 완료")
            
            # PIL Image로 변환
            img = Image.open(io.BytesIO(png))
            logger.info("PIL Image로 변환 완료")
            
            # 이미지 리사이즈 (OpenAI API 제한에 맞춤)
            img.thumbnail((2000, 2000))
            logger.info("이미지 리사이즈 완료")
            
            # 현재 시간을 파일명에 포함
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upbit_chart_{current_time}.png"
            
            # 현재 스크립트의 경로를 가져옴
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 파일 저장 경로 설정
            file_path = os.path.join(script_dir, filename)
            
            # 이미지 파일로 저장
            img.save(file_path)
            logger.info(f"스크린샷이 저장되었습니다: {file_path}")
            
            # 이미지를 바이트로 변환
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            logger.info("이미지를 바이트로 변환 완료")
            
            # base64로 인코딩
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            logger.info("base64 인코딩 완료")
            
            return base64_image, file_path
        except WebDriverException as wde:
            logger.error(f"WebDriver 예외 발생: {wde}")
            self.driver.save_screenshot("error_webdriver_exception.png")
            return None, None
        except IOError as ioe:
            logger.error(f"I/O 예외 발생: {ioe}")
            self.driver.save_screenshot("error_io_exception.png")
            return None, None
        except Exception as e:
            logger.error(f"스크린샷 캡처 및 인코딩 중 오류 발생: {e}")
            self.driver.save_screenshot("error_screenshot_capture.png")
            return None, None

    def test_chart_capture(self):
        base64_image = None
        file_path = None
        try:
            logger.info("테스트 시작...")
            self.driver.get("https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC")
            
            # 페이지 로드 대기
            logger.info("페이지 로드 대기 중...")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "cq-chart-title"))
            )
            logger.info("페이지 로드 완료")

            self.perform_chart_actions()

            base64_image, file_path = self.capture_and_encode_screenshot()
            
            self.assertIsNotNone(base64_image, "Screenshot was not captured successfully")
            self.assertIsNotNone(file_path, "Screenshot file path is None")
            self.assertTrue(os.path.exists(file_path), "Screenshot file was not saved")
            
            logger.info("Chart capture test completed successfully")

        except AssertionError as ae:
            logger.error(f"Assertion Error: {str(ae)}")
            self.driver.save_screenshot("assertion_error_screenshot.png")
            raise

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            self.driver.save_screenshot("error_screenshot.png")
            raise

        # finally:
        #     # 테스트 종료 후 파일 정리
        #     if file_path and os.path.exists(file_path):
        #         os.remove(file_path)
        #     for error_file in ["error_screenshot.png", "error_screenshot_capture.png", "assertion_error_screenshot.png", "error_webdriver_exception.png", "error_io_exception.png"]:
        #         if os.path.exists(error_file):
        #             os.remove(error_file)