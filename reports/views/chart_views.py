from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paw_drf.tasks import capture_and_analyze_chart_task
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def capture_and_analyze_chart(request):
    try:
        task = capture_and_analyze_chart_task.delay()
        return JsonResponse({
            'success': True,
            'message': 'Chart capture and analysis task has been initiated.',
            'task_id': task.id
        })
    except Exception as e:
        logger.error(f"Error initiating chart capture and analysis task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)