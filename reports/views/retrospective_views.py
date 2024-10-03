import logging
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..services import OpenAIService, RetrospectiveReportService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@csrf_exempt
def create_and_analyze_retrospective_report(request):
    if request.method == 'POST':
        try:
            prompt, main_report_id = RetrospectiveReportService.create_retrospective_prompt()
            
            openai_service = OpenAIService()
            analysis_result = openai_service.analyze_retrospective_report(prompt)
            
            if 'error' in analysis_result:
                logger.error(f"Error in OpenAI analysis: {analysis_result['error']}")
                return JsonResponse({'error': analysis_result['error']}, status=500)
            
            new_weights, message = RetrospectiveReportService.analyze_and_update_weights(analysis_result, main_report_id)
            
            if new_weights:
                return JsonResponse({
                    'success': True,
                    'message': '회고 분석 보고서가 생성되고 가중치가 업데이트되었습니다.',
                    'new_weights': new_weights.to_dict(),
                    'main_report_id': main_report_id
                })
            else:
                logger.error(f"Weight update failed: {message}")
                return JsonResponse({'error': message}, status=500)
        
        except Exception as e:
            logger.error(f"회고 분석 및 가중치 업데이트 중 오류 발생: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)
