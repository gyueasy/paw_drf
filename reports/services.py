from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from django.conf import settings
from openai import OpenAI
from PIL import Image
import os
import time
import logging
import requests
import io
import base64
import json
from datetime import datetime
from .gpt_prompts import get_chart_analysis_prompt, get_news_analysis_prompt, get_report_weights_prompt, get_main_report_prompt
from .models import MainReport, ReportWeights, ChartReport, NewsReport



logger = logging.getLogger(__name__)


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

class ChartService:
    def __init__(self):
        self.driver = None

    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def capture_chart(self):
        try:
            self.create_driver()
            self.driver.get("https://upbit.com/full_chart?code=CRIX.UPBIT.KRW-BTC")
            logger.info("페이지 로드 완료")
            time.sleep(10)
            logger.info("차트 작업 시작")
            self._perform_chart_actions()
            logger.info("차트 작업 완료")
            image_url = self._capture_and_save_screenshot()
            if image_url:
                logger.info(f"스크린샷 캡처 완료. 이미지 URL: {image_url}")
                return image_url
            else:
                logger.error("스크린샷 캡처 실패")
                return None
        except Exception as e:
            logger.error(f"차트 캡처 중 오류 발생: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def _click_element_by_xpath(self, xpath, element_name, wait_time=30):
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
                "//*[@id='fullChartiq']/div/div/div[1]/div/div/cq-menu[3]",
                "지표 메뉴"
            )
            self._click_indicator_option(indicator_xpath, indicator_name)

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

class NewsService:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

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
        self.driver.quit()

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_chart(self, file_path):
        with open(file_path, "rb") as image_file:
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
                                "text": get_chart_analysis_prompt()
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
            logger.info(f"Raw API response: {content}")
            
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1:
                content = content[json_start:json_end+1]
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            logger.error(f"Problematic content: {content}")
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"Error in analyze_chart: {str(e)}")
            return {"error": f"Error analyzing chart: {str(e)}"}
        
    def analyze_news(self, news_items):
        try:
            news_content = json.dumps(news_items, ensure_ascii=False)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cryptocurrency news analyst."
                    },
                    {
                        "role": "user",
                        "content": f"{get_news_analysis_prompt()}\n\nHere are the news items:\n{news_content}\n\nProvide your analysis in the following JSON format:\n{{\"market_sentiment\": \"\", \"key_events\": [], \"potential_impact\": \"\", \"notable_trends\": []}}"
                    }
                ],
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            # 백틱과 ```json 제거
            cleaned_analysis = analysis.strip().strip('```json').strip('```')

            logger.info(f"News analysis raw content: {cleaned_analysis[:100]}...")
            
            # JSON 디코딩
            return json.loads(cleaned_analysis)

        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error in analyze_news: {str(e)}")
            logger.error(f"Problematic content: {cleaned_analysis}")
            return {"error": f"Invalid JSON in API response: {str(e)}"}
        except Exception as e:
            logger.error(f"Error in analyze_news: {str(e)}")
            return {"error": f"Error analyzing news: {str(e)}"}
        
    def adjust_weights(self, main_report):
        previous_reports = main_report.previous_reports
        current_weights = main_report.latest_weights

        prompt = get_report_weights_prompt(main_report, previous_reports, current_weights)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant tasked with adjusting weights for a financial report based on previous report accuracies and current market conditions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                n=1,
                temperature=0.5,
            )

            gpt_response = response.choices[0].message.content.strip()

            new_weights, reason = self._parse_weight_adjustment_response(gpt_response)

            new_report_weights = ReportWeights(
                main_report=main_report,
                reason=reason,
                **new_weights
            )
            new_report_weights.save()

            return new_report_weights

        except Exception as e:
            print(f"GPT를 사용한 가중치 조정 중 오류 발생: {str(e)}")
            return None

    def _parse_weight_adjustment_response(self, gpt_response):
        # GPT 응답을 파싱하는 로직 구현
        # 예시:
        new_weights = {
            'overall_weight': 1.0,
            'market_weight': 1.0,
            # ... 다른 가중치들 ...
        }
        reason = "GPT가 제공한 가중치 조정 이유"
        
        return new_weights, reason
    
    def get_main_report_analysis(self, prompt, analysis_input):
        try:
            def json_serial(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError("Type not serializable")

            analysis_input_json = json.dumps(analysis_input, default=json_serial)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant tasked with analyzing financial market data and providing investment recommendations."},
                    {"role": "user", "content": f"{prompt}\n\nHere's the data to analyze:\n{analysis_input_json}"}
                ],
                max_tokens=1000,
                n=1,
                temperature=0.5,
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error in get_main_report_analysis: {str(e)}")
            return {"error": f"Error analyzing main report data: {str(e)}"}
    
class ReportService:
    def __init__(self):
        self.openai_service = OpenAIService()

    def preprocess_data(self, data):
        chart_analysis = data['chart_analysis']
        market_analysis = data['market_analysis']
        weights = data['weights']

        preprocessed_text = "Chart Analysis:\n"
        for key, value in chart_analysis.items():
            if isinstance(value, dict):
                preprocessed_text += f"- {key.replace('_', ' ').title()}: {value['analysis']} (Recommendation: {value['recommendation']})\n"
            else:
                preprocessed_text += f"- {key.replace('_', ' ').title()}: {value}\n"

        preprocessed_text += "\nMarket Analysis:\n"
        preprocessed_text += f"- News Sentiment: {market_analysis['news_analysis']['market_sentiment']}\n"
        preprocessed_text += "- Key Events:\n"
        for event in market_analysis['news_analysis']['key_events'][:3]:
            preprocessed_text += f"  * {event['title']} (Impact: {event['impact_percentage']}%)\n"
        preprocessed_text += f"- Potential Impact: {market_analysis['news_analysis']['potential_impact']}\n"
        preprocessed_text += "- Notable Trends:\n"
        for trend in market_analysis['news_analysis']['notable_trends']:
            preprocessed_text += f"  * {trend}\n"
        
        fng = market_analysis['fear_and_greed_index']
        preprocessed_text += f"- Fear and Greed Index: {fng['value']} ({fng['value_classification']})\n"

        preprocessed_text += f"\nWeights: {weights}\n"

        return preprocessed_text

    def create_main_report(self):
        latest_chart_report = ChartReport.objects.latest('timestamp')
        latest_news_report = NewsReport.objects.latest('created_at')
        latest_weights = ReportWeights.objects.latest('created_at') if ReportWeights.objects.exists() else None
        
        fng_index = get_fear_and_greed_index()
        
        input_data = {
            "chart_analysis": {
                "technical_analysis": latest_chart_report.technical_analysis,
                "candlestick_analysis": latest_chart_report.candlestick_analysis,
                "moving_average_analysis": latest_chart_report.moving_average_analysis,
                "bollinger_bands_analysis": latest_chart_report.bollinger_bands_analysis,
                "rsi_analysis": latest_chart_report.rsi_analysis,
                "fibonacci_retracement_analysis": latest_chart_report.fibonacci_retracement_analysis,
                "macd_analysis": latest_chart_report.macd_analysis,
                "support_resistance_analysis": latest_chart_report.support_resistance_analysis,
                "overall_recommendation": latest_chart_report.overall_recommendation
            },
            "market_analysis": {
                "news_analysis": json.loads(latest_news_report.news_analysis),
                "fear_and_greed_index": {
                    "value": fng_index["value"],
                    "value_classification": fng_index["value_classification"],
                    "timestamp": fng_index["timestamp"].isoformat() if isinstance(fng_index["timestamp"], datetime) else fng_index["timestamp"],
                    "time_until_update": fng_index["time_until_update"]
                }
            },
            "weights": {
                "overall_weight": latest_weights.overall_weight,
                "market_weight": latest_weights.market_weight,
                "news_weight": latest_weights.news_weight,
                "chart_overall_weight": latest_weights.chart_overall_weight,
                "chart_technical_weight": latest_weights.chart_technical_weight,
                "chart_candlestick_weight": latest_weights.chart_candlestick_weight,
                "chart_moving_average_weight": latest_weights.chart_moving_average_weight,
                "chart_bollinger_bands_weight": latest_weights.chart_bollinger_bands_weight,
                "chart_rsi_weight": latest_weights.chart_rsi_weight,
                "chart_fibonacci_weight": latest_weights.chart_fibonacci_weight,
                "chart_macd_weight": latest_weights.chart_macd_weight,
                "chart_support_resistance_weight": latest_weights.chart_support_resistance_weight
            } if latest_weights else "No previous weights available."
        }
        
        preprocessed_data = self.preprocess_data(input_data)
        prompt = get_main_report_prompt()
        final_message = f"{prompt}\n\nHere's the data to analyze:\n{preprocessed_data}"
        
        # Create main_report_input.txt file
        with open('main_report_input.txt', 'w', encoding='utf-8') as f:
            f.write(final_message)
        
        gpt_response = self.openai_service.get_main_report_analysis(prompt, preprocessed_data)
        
        main_report = MainReport.objects.create(
            title=gpt_response['title'],  # GPT가 생성한 제목 사용, 테스트중...
            overall_analysis=gpt_response['overall_analysis'],
            market_analysis=gpt_response['market_analysis'],
            chart_analysis=gpt_response['chart_analysis'],
            recommendation=gpt_response['recommendation'],
            confidence_level=gpt_response['confidence_level'],
            reasoning=gpt_response['reasoning']
        )
        return main_report