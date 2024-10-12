네, 이해했습니다. `news_service`와 `chart_service`의 구동 방식을 완전히 동일하게 맞추는 것이 좋겠습니다. 문제는 `news_service`에서 웹 요소를 찾지 못하고 있는 것 같습니다. 다음과 같이 `news_service.py`를 수정해 보겠습니다:

```python
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.driver = None

    def create_driver(self):
        logger.info("ChromeDriver 설정 중...")
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            service = Service('/usr/local/bin/chromedriver')

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            return self.driver
        except Exception as e:
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}", exc_info=True)
            raise

    def crawl_news(self):
        try:
            self.driver = self.create_driver()
            bitcoin_url = "https://www.google.com/search?q=bitcoin+news+today&tbm=nws&tbs=qdr:d"
            altcoin_url = "https://www.google.com/search?q=altcoin+news&tbm=nws&tbs=qdr:d"
            
            news_items = []
            news_items.extend(self._crawl_single_page(bitcoin_url, "Bitcoin"))
            news_items.extend(self._crawl_single_page(altcoin_url, "Altcoin"))
            
            return news_items
        except Exception as e:
            logger.error(f"뉴스 크롤링 중 오류 발생: {e}", exc_info=True)
            return []
        finally:
            self._quit_driver()

    def _crawl_single_page(self, url, category):
        self.driver.get(url)
        logger.info(f"{category} 뉴스 페이지 로드 완료")
        time.sleep(5)  # 페이지 로드를 위한 대기 시간 추가
        news_items = []
        
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SoaBEf"))
            )
            news_elements = self.driver.find_elements(By.CLASS_NAME, "SoaBEf")
            
            for element in news_elements[:10]:  # 최대 10개의 뉴스 아이템만 크롤링
                try:
                    title = element.find_element(By.CLASS_NAME, "r_znxjsd").text
                    summary = element.find_element(By.CLASS_NAME, "GI74Re").text
                    date_source = element.find_element(By.CLASS_NAME, "OSrXXb").text
                    date, source = date_source.split(' - ')
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'date': date,
                        'source': source,
                        'category': category
                    })
                except NoSuchElementException as e:
                    logger.warning(f"Error crawling {category} news item: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error crawling {category} news item: {str(e)}", exc_info=True)
            
            logger.info(f"{len(news_items)}개의 {category} 뉴스 아이템 크롤링 완료")
        except TimeoutException:
            logger.error(f"{category} 뉴스 요소를 찾는 데 시간 초과")
        except Exception as e:
            logger.error(f"{category} 뉴스 크롤링 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        
        return news_items

    def _quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("ChromeDriver 종료")
