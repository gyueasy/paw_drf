from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services.chart_service import ChartService
import logging 
from django.core.exceptions import PermissionDenied

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
def capture_and_analyze_chart(request):
    try:
        if request.method == 'POST':
            chart_service = ChartService()
            result = chart_service.capture_and_analyze_chart()

            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=500)
            
            return JsonResponse(result)

        return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)
    except PermissionDenied as e:
        logger.error(f"PermissionDenied: {str(e)}")
        return JsonResponse({'error': 'Access Denied'}, status=403)