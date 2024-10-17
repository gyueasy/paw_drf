import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paw_drf.tasks import crawl_and_analyze_news_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def crawl_and_analyze_news(request):
    try:
        task = crawl_and_analyze_news_task.delay()
        return JsonResponse({
            'success': True,
            'message': 'News crawling and analysis task has been initiated.',
            'task_id': task.id
        })
    except Exception as e:
        logger.error(f"Error initiating news crawling and analysis task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)