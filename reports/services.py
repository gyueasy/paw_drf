from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
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
from decimal import Decimal
from .gpt_prompts import get_chart_analysis_prompt, get_news_analysis_prompt, get_retrospective_analysis_prompt_template, get_main_report_prompt, basic_retrospective_analysis_prompt
from .models import MainReport, ReportWeights, ChartReport, NewsReport, Price, Accuracy
from .utils import get_current_price, calculate_price_change

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
        
    def get_main_report_analysis(self, prompt, analysis_input):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant tasked with analyzing financial market data and providing investment recommendations."},
                    {"role": "user", "content": f"{prompt}\n\nHere's the data to analyze:\n{analysis_input}"}
                ],
                max_tokens=1000,
                n=1,
                temperature=0.5,
            )
            
            content = response.choices[0].message.content
            logger.info(f"Raw API response: {content}")
            # JSON 형식으로 변환
            try:
                parsed_content = json.loads(content)
                return parsed_content
            except json.JSONDecodeError:
                # JSON 파싱에 실패한 경우, 문자열을 직접 파싱
                logger.warning("Failed to parse JSON, attempting manual parsing")
                parsed_content = {}
                for line in content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        parsed_content[key.strip()] = value.strip()
                return parsed_content

        except Exception as e:
            logger.error(f"Error in get_main_report_analysis: {str(e)}")
            return {"error": f"Error analyzing main report data: {str(e)}"}
        
    def analyze_retrospective_report(self, report_content):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant tasked with analyzing a retrospective report and suggesting weight adjustments for various factors in cryptocurrency market analysis."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this retrospective report, suggest adjustments to the weights of different analysis factors. Provide your response in JSON format with 'reasoning' and 'weight_adjustments'.\n\nReport:\n{report_content}"
                    }
                ],
                max_tokens=1000
            )

            analysis = response.choices[0].message.content
            logger.info(f"Raw API response content: {analysis}")
            
            # 백틱과 ```json 제거
            cleaned_analysis = analysis.strip().strip('```json').strip('```')
            
            # JSON 파싱
            parsed_content = json.loads(cleaned_analysis)
            
            if 'weight_adjustments' not in parsed_content:
                raise ValueError("Missing 'weight_adjustments' in API response")
            
            # 응답을 파일로 저장, 테스트용
            with open('retrospective_report.txt', 'w', encoding='utf-8') as f:
                f.write(f"Raw API response:\n{analysis}\n\n")
                f.write(f"Cleaned and parsed response:\n{json.dumps(parsed_content, indent=2)}")
        
            
            return parsed_content

        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            logger.error(f"Problematic content: {cleaned_analysis}")
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"Error in analyze_retrospective_report: {str(e)}")
            return {"error": f"Error analyzing retrospective report: {str(e)}"}


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
        try:
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
                    "fear_greed_index_weight": latest_weights.fear_greed_index_weight,
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
            
            if 'error' in gpt_response:
                logger.error(f"Error in GPT response: {gpt_response['error']}")
                return None


            main_report = MainReport(
                title=gpt_response.get('title', 'Default Report Title'),
                overall_analysis=gpt_response.get('overall_analysis', ''),
                market_analysis=gpt_response.get('market_analysis', ''),
                chart_analysis=gpt_response.get('chart_analysis', ''),
                recommendation=gpt_response.get('recommendation', ''),
                confidence_level=gpt_response.get('confidence_level', ''),
                reasoning=gpt_response.get('reasoning', ''),
                chart_report_id=latest_chart_report.id if latest_chart_report else None,
                news_report_id=latest_news_report.id if latest_news_report else None,
                weights_id=latest_weights.id if latest_weights else None
            )
            main_report.save()

            logger.info(f"Successfully created and saved MainReport with id: {main_report.id}")
            return main_report
        except Exception as e:
            logger.error(f"Error in create_main_report: {str(e)}")
            return None
    
class RetrospectiveReportService:
    @staticmethod
    def get_latest_data():
        main_report = MainReport.objects.order_by('-created_at').first()
        weights = ReportWeights.objects.order_by('-created_at').first()
        current_price = Price.objects.order_by('-timestamp').first()
        logger.info(f"Latest Price: {current_price}")
        logger.info(f"Latest Weights: {weights}")

        return main_report, weights, current_price

    @staticmethod
    def create_default_weights(main_report):
        default_weights = {
            'overall_weight': 1.0,
            'fear_greed_index_weight': 1.0,
            'news_weight': 1.0,
            'chart_overall_weight': 1.0,
            'chart_technical_weight': 1.0,
            'chart_candlestick_weight': 1.0,
            'chart_moving_average_weight': 1.0,
            'chart_bollinger_bands_weight': 1.0,
            'chart_rsi_weight': 1.0,
            'chart_fibonacci_weight': 1.0,
            'chart_macd_weight': 1.0,
            'chart_support_resistance_weight': 1.0
        }
        return ReportWeights.objects.create(main_report=main_report, **default_weights)

    @staticmethod
    def create_retrospective_prompt():
        main_report = MainReport.objects.order_by('-created_at').first()
        latest_accuracy = Accuracy.objects.order_by('-calculated_at').first()
        current_price = Price.objects.order_by('-timestamp').first()
        
        if not main_report or not current_price or not latest_accuracy:
            logger.warning("No sufficient data for thorough analysis. Returning basic retrospective prompt.")
            return basic_retrospective_analysis_prompt(), None

        avg_accuracy = Accuracy.objects.aggregate(models.Avg('accuracy'))['accuracy__avg']
        if avg_accuracy is not None:
            avg_accuracy *= 100  # 퍼센트로 변환

        previous_price = Price.objects.filter(timestamp__lt=current_price.timestamp).order_by('-timestamp').first()
        
        prompt_template = get_retrospective_analysis_prompt_template()
        
        format_dict = {
            "current_price": current_price.trade_price if current_price else "N/A",
            "previous_price": previous_price.trade_price if previous_price else "N/A",
            "price_change": f"{latest_accuracy.price_change:.2f}%" if latest_accuracy else "N/A",
            "current_accuracy": f"{latest_accuracy.accuracy:.2f}" if latest_accuracy else "N/A",
            "avg_accuracy": f"{avg_accuracy:.2f}%" if avg_accuracy is not None else "N/A",
            "recommendation": latest_accuracy.recommendation if latest_accuracy else "N/A",
            "recommendation_value": latest_accuracy.recommendation_value if latest_accuracy else "N/A",
            "is_correct": "Yes" if latest_accuracy and latest_accuracy.is_correct else "No",
            "main_report": main_report,
        }

        prompt = prompt_template.format(**format_dict)
        
        logger.info(f"Generated prompt: {prompt[:200]}...")  # 로그에 생성된 프롬프트의 일부를 출력

        # 프롬프트를 파일로 저장, 테스트단계에서 확인하기 위함
        with open('retrospective_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(prompt)

        return prompt, main_report.id if main_report else None

    @staticmethod
    def analyze_and_update_weights(analysis_result, main_report_id=None):
        try:
            weight_adjustments = analysis_result['weight_adjustments']
            reasoning = analysis_result['reasoning']

            latest_weights = ReportWeights.objects.order_by('-created_at').first()

            new_weights = ReportWeights(
                reasoning=reasoning
            )

            for field in ReportWeights._meta.get_fields():
                if field.name.endswith('_weight'):
                    current_value = getattr(latest_weights, field.name, 1.0) if latest_weights else 1.0
                    adjustment = weight_adjustments.get(field.name, 0)
                    setattr(new_weights, field.name, current_value + adjustment)

            new_weights.save()
            return new_weights, reasoning
        except Exception as e:
            logger.error(f"OpenAI API 요청 중 오류 발생: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def create_and_update_retrospective_report():
        prompt, main_report_id = RetrospectiveReportService.create_retrospective_prompt()
        if prompt is None:
            return None, "회고 분석을 위한 프롬프트를 생성할 수 없습니다."
        
        new_weights, message = RetrospectiveReportService.analyze_and_update_weights(prompt, main_report_id)
        if new_weights:
            return new_weights, "회고 분석 및 가중치 업데이트가 성공적으로 완료되었습니다."
        else:
            return None, f"가중치 업데이트 실패: {message}"