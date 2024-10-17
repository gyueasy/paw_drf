import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from paw_drf.tasks import create_main_report_task
from ..services import ReportService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

report_service = ReportService()

@csrf_exempt
@require_http_methods(["POST"])
def create_main_report(request):
    try:
        task = create_main_report_task.delay()
        return JsonResponse({
            'success': True,
            'message': '메인 리포트 생성 작업이 시작되었습니다.',
            'task_id': task.id
        })
    except Exception as e:
        logger.error(f"Error initiating main report creation task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_latest_main_report(request):
    report = report_service.get_latest_main_report()
    if report is None:
        return JsonResponse({'error': '메인 리포트가 없습니다.'}, status=404)
    
    return JsonResponse({
        'id': report.id,
        'title': report.title,
        'overall_analysis': report.overall_analysis,
        'created_at': report.created_at.isoformat()
    })

def get_main_report_by_id(request, report_id):
    report = report_service.get_main_report_by_id(report_id)
    if report is None:
        return JsonResponse({'error': '해당 ID의 메인 리포트가 없습니다.'}, status=404)
    
    return JsonResponse({
        'id': report.id,
        'title': report.title,
        'overall_analysis': report.overall_analysis,
        'market_analysis': report.market_analysis,
        'chart_analysis': report.chart_analysis,
        'recommendation': report.recommendation,
        'confidence_level': report.confidence_level,
        'reasoning': report.reasoning,
        'created_at': report.created_at.isoformat()
    })