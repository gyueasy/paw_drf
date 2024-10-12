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
        time.sleep(10)  # 페이지 로드를 위한 대기 시간 증가
        news_items = []
        
        try:
            for i in range(1, 11):  # 10개의 뉴스 아이템 크롤링
                try:
                    source_xpath = f"/html/body/div[3]/div/div[11]/div/div[2]/div[2]/div/div/div/div/div[{i}]/div/div/a/div/div[2]/div[1]/span"
                    title_xpath = f"/html/body/div[3]/div/div[11]/div/div[2]/div[2]/div/div/div/div/div[{i}]/div/div/a/div/div[2]/div[2]"
                    summary_xpath = f"/html/body/div[3]/div/div[11]/div/div[2]/div[2]/div/div/div/div/div[{i}]/div/div/a/div/div[2]/div[3]"
                    date_xpath = f"/html/body/div[3]/div/div[11]/div/div[2]/div[2]/div/div/div/div/div[{i}]/div/div/a/div/div[2]/div[4]"
                    
                    source = self.driver.find_element(By.XPATH, source_xpath).text
                    title = self.driver.find_element(By.XPATH, title_xpath).text
                    summary = self.driver.find_element(By.XPATH, summary_xpath).text
                    date = self.driver.find_element(By.XPATH, date_xpath).text
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'date': date,
                        'source': source,
                        'category': category
                    })
                    logger.info(f"{category} 뉴스 아이템 {i} 크롤링 완료")
                except NoSuchElementException as e:
                    logger.warning(f"Error crawling {category} news item {i}: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error crawling {category} news item {i}: {str(e)}", exc_info=True)
            
            logger.info(f"{len(news_items)}개의 {category} 뉴스 아이템 크롤링 완료")
        except Exception as e:
            logger.error(f"{category} 뉴스 크롤링 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
        
        return news_items

    def _quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("ChromeDriver 종료")
