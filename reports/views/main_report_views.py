import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services import ReportService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@csrf_exempt
def create_main_report(request):
    if request.method == 'POST':
        try:
            report_service = ReportService()
            main_report = report_service.create_main_report()
            if main_report:
                return JsonResponse({
                    'success': True,
                    'message': '메인 리포트가 성공적으로 생성되었습니다.',
                    'report_id': main_report.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '메인 리포트 생성에 실패했습니다.'
                }, status=500)
        except Exception as e:
            logger.error(f"Error in create_main_report view: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'메인 리포트 생성 중 오류가 발생했습니다: {str(e)}'
            }, status=500)
    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)

