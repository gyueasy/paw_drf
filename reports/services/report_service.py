# 파이썬 표준 라이브러리
import logging
import json
from datetime import datetime

# 서드파티 라이브러리
from selenium.webdriver.support import expected_conditions as EC

# 장고 관련 임포트
from django.db import models
from django.core.cache import cache

# 로컬 애플리케이션 임포트
from ..gpt_prompts import (
    get_retrospective_analysis_prompt_template,
    get_main_report_prompt,
    basic_retrospective_analysis_prompt
)
from ..models import MainReport, ReportWeights, ChartReport, NewsReport, Price, Accuracy
from ..services.openai_service import OpenAIService
from ..utils import get_fear_and_greed_index

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.openai_service = OpenAIService()

    @staticmethod
    def get_cache_key(key):
        return f"mainreport:{key}"

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

            # 캐시 업데이트
            self.update_report_cache(main_report)

            logger.info(f"Successfully created and saved MainReport with id: {main_report.id}")
            return main_report
        except Exception as e:
            logger.error(f"Error in create_main_report: {str(e)}")
            return None
        
    def update_report_cache(self, report):
        cache.set(self.get_cache_key('latest'), report, timeout=3600)  # 1시간 캐시
        cache.set(self.get_cache_key(f'id:{report.id}'), report, timeout=3600)

    def invalidate_report_cache(self, report_id):
        cache.delete(self.get_cache_key(f'id:{report_id}'))
        cache.delete(self.get_cache_key('latest'))

    def get_latest_main_report(self):
        cache_key = self.get_cache_key('latest')
        report = cache.get(cache_key)
        if report is None:
            try:
                report = MainReport.objects.latest('created_at')
                self.update_report_cache(report)
            except MainReport.DoesNotExist:
                return None
        return report

    def get_main_report_by_id(self, report_id):
        cache_key = self.get_cache_key(f'id:{report_id}')
        report = cache.get(cache_key)
        if report is None:
            try:
                report = MainReport.objects.get(id=report_id)
                self.update_report_cache(report)
            except MainReport.DoesNotExist:
                return None
        return report


        
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
        
        openai_service = OpenAIService()
        analysis_result = openai_service.analyze_retrospective_report(prompt)
        
        if 'error' in analysis_result:
            return None, f"OpenAI 분석 중 오류 발생: {analysis_result['error']}"
        
        new_weights, message = RetrospectiveReportService.analyze_and_update_weights(analysis_result, main_report_id)
        if new_weights:
            return new_weights, "회고 분석 및 가중치 업데이트가 성공적으로 완료되었습니다."
        else:
            return None, f"가중치 업데이트 실패: {message}"