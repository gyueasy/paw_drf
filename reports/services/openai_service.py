# 파이썬 표준 라이브러리
import logging
import base64
import json
import httpx
import asyncio

# 서드파티 라이브러리
from selenium.webdriver.support import expected_conditions as EC
# from openai import AsyncOpenAI
from openai import OpenAI

# 장고 관련 임포트
from django.conf import settings


# 로컬 애플리케이션 임포트
from ..gpt_prompts import (
    get_chart_analysis_prompt,
    get_news_analysis_prompt,
)

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=httpx.Client(timeout=60)
        )

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
