from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paw_drf.tasks import calculate_accuracy_task
from celery.result import AsyncResult

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_accuracy(request):
    task = calculate_accuracy_task.delay()
    return JsonResponse({
        'success': True,
        'message': 'Accuracy calculation task has been initiated.',
        'task_id': task.id
    })

@require_http_methods(["GET"])
def get_accuracy_result(request, task_id):
    task_result = AsyncResult(task_id)
    if task_result.ready():
        result = task_result.result
        if isinstance(result, Exception):
            return JsonResponse({
                'success': False,
                'error': str(result)
            }, status=500)
        return JsonResponse({
            'success': True,
            'result': result
        })
    else:
        return JsonResponse({
            'success': True,
            'status': 'PENDING'
        })