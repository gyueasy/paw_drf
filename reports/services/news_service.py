# 파이썬 표준 라이브러리
import logging

# 서드파티 라이브러리
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.driver = None
        self.create_driver()

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
        except Exception as e:
            logger.error(f"ChromeDriver 생성 중 오류 발생: {e}")
            raise

    def crawl_news(self):
        bitcoin_url = "https://www.google.com/search?q=bitcoin+news+today&sca_esv=4c3d1b1066869309&sca_upv=1&tbm=nws&sxsrf=ADLYWIK8x3D2LUNcBVUwNscEcDrQQrhyEQ:1727580522901&source=lnt&tbs=qdr:d&sa=X&ved=2ahUKEwi-sI37mueIAxWt2TQHHaU1MhcQpwV6BAgCEA0&biw=1049&bih=957&dpr=1.25"
        altcoin_url = "https://www.google.com/search?q=altcoin+news&sca_esv=4c3d1b1066869309&sca_upv=1&biw=1049&bih=957&tbs=qdr%3Ad&tbm=nws&sxsrf=ADLYWIIOSOPtMydv_8A9EPI9d1UuoKUMSA%3A1727581719175&ei=F874ZseyCv3f2roPq6eWwQM&ved=0ahUKEwiHmsS1n-eIAxX9r1YBHauTJTgQ4dUDCA0&uact=5&oq=altcoin+news&gs_lp=Egxnd3Mtd2l6LW5ld3MiDGFsdGNvaW4gbmV3czIFEAAYgAQyBBAAGB4yBBAAGB4yBBAAGB4yBhAAGAgYHjIGEAAYCBgeMgYQABgIGB4yBhAAGAgYHjIGEAAYBRgeMgYQABgFGB5IiylQgCBYkihwAXgAkAEAmAGRAaABhwWqAQMyLjS4AQPIAQD4AQGYAgegAsUFwgIKEAAYgAQYQxiKBZgDAIgGAZIHAzMuNKAHsCA&sclient=gws-wiz-news"
        
        news_items = []
        news_items.extend(self._crawl_single_page(bitcoin_url, "Bitcoin"))
        news_items.extend(self._crawl_single_page(altcoin_url, "Altcoin"))
        
        return news_items

    def _crawl_single_page(self, url, category):
        self.driver.get(url)
        news_items = []
        
        for i in range(1, 11):  # 각 페이지에서 10개의 뉴스 아이템을 크롤링
            try:
                title = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[@id='rso']/div/div/div[{i}]/div/div/a/div/div[2]/div[2]"))
                ).text
                summary = self.driver.find_element(By.XPATH, f"//*[@id='rso']/div/div/div[{i}]/div/div/a/div/div[2]/div[3]").text
                date = self.driver.find_element(By.XPATH, f"//*[@id='rso']/div/div/div[{i}]/div/div/a/div/div[2]/div[4]").text
                source = self.driver.find_element(By.XPATH, f"//*[@id='rso']/div/div/div[{i}]/div/div/a/div/div[2]/div[1]/span").text
                
                news_items.append({
                    'title': title,
                    'summary': summary,
                    'date': date,
                    'source': source,
                    'category': category
                })
            except Exception as e:
                logger.error(f"Error crawling {category} news item {i}: {str(e)}")
        
        return news_items

    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
