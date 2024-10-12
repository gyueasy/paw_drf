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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

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
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
            logger.error(f"상세 오류: {traceback.format_exc()}")
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
            logger.error(f"뉴스 크롤링 중 오류 발생: {e}\n{traceback.format_exc()}")
            return []
        finally:
            self._quit_driver()

    def _crawl_single_page(self, url, category):
        self.driver.get(url)
        news_items = []
        
        for i in range(1, 11):  # 각 페이지에서 10개의 뉴스 아이템을 크롤링
            try:
                title = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='SoaBEf']/div[{i}]//h3[@class='r_znxjsd']"))
                ).text
                summary = self.driver.find_element(By.XPATH, f"//div[@class='SoaBEf']/div[{i}]//div[@class='GI74Re nDgy9d']").text
                date_source = self.driver.find_element(By.XPATH, f"//div[@class='SoaBEf']/div[{i}]//div[@class='OSrXXb ZE0LJd']").text
                date, source = date_source.split(' - ')
                
                news_items.append({
                    'title': title,
                    'summary': summary,
                    'date': date,
                    'source': source,
                    'category': category
                })
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"Error crawling {category} news item {i}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error crawling {category} news item {i}: {str(e)}")
        
        return news_items

    def _quit_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None