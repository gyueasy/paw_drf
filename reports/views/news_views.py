# Python standard library imports
import json
import logging

# Django imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Local application imports
from ..models import NewsReport
from ..services import OpenAIService, NewsService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
def crawl_and_analyze_news(request):
    if request.method == 'POST':
        try:
            news_service = NewsService()
            news_items = news_service.crawl_news()
            
            openai_service = OpenAIService()
            analysis_result = openai_service.analyze_news(news_items)
            
            if "error" in analysis_result:
                logger.error(f"Analysis error: {analysis_result['error']}")
                return JsonResponse({'error': analysis_result["error"]}, status=500)
            
            news_report = NewsReport(
                news_analysis=json.dumps(analysis_result)
            )
            news_report.save()
            
            return JsonResponse({
                'success': True,
                'message': '뉴스가 성공적으로 크롤링, 분석 및 저장되었습니다.',
                'news_report_id': news_report.id,
                'created_at': news_report.created_at.isoformat(),
                'analysis_summary': {
                    'market_sentiment': analysis_result.get('market_sentiment', ''),
                    'key_events_count': len(analysis_result.get('key_events', [])),
                    'potential_impact': analysis_result.get('potential_impact', ''),
                    'notable_trends_count': len(analysis_result.get('notable_trends', []))
                }
            })

        except Exception as e:
            logger.error(f"뉴스 크롤링 및 분석 중 오류 발생: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)

