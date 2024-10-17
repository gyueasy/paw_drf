import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paw_drf.tasks import create_and_analyze_retrospective_report_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def create_and_analyze_retrospective_report(request):
    try:
        task = create_and_analyze_retrospective_report_task.delay()
        return JsonResponse({
            'success': True,
            'message': 'Retrospective report analysis task has been initiated.',
            'task_id': task.id
        })
    except Exception as e:
        logger.error(f"Error initiating retrospective report analysis task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)