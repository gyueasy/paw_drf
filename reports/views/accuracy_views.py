# 파이썬 표준 라이브러리
import logging

# 서드파티 라이브러리
# 장고 관련 임포트
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# 로컬 애플리케이션 임포트
from ..models import MainReport, Price, Accuracy
from ..serializers import SevenDayAverageAccuracySerializer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@csrf_exempt
@require_http_methods(["POST"])
def calculate_accuracy(request):
    try:
        new_accuracy = Accuracy.calculate_and_save_accuracy()
        
        return JsonResponse({
            'success': True,
            'message': 'Accuracy calculated and saved successfully.',
            'accuracy': new_accuracy.accuracy,
            'average_accuracy': f"{new_accuracy.average_accuracy:.2f}%",
            'recommendation': new_accuracy.recommendation,
            'recommendation_value': new_accuracy.recommendation_value,
            'price_change': f"{new_accuracy.price_change:.2f}%",
            'is_correct': new_accuracy.is_correct,
            'calculated_at': new_accuracy.calculated_at,
            'db_stats': {
                'main_reports_count': MainReport.objects.count(),
                'prices_count': Price.objects.count(),
                'accuracies_count': Accuracy.objects.count()
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    

@api_view(['GET'])
def get_seven_day_average_accuracy(request):
    try:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        seven_day_accuracy = Accuracy.objects.filter(
            calculated_at__range=(start_date, end_date)
        ).aggregate(avg_accuracy=Avg('average_accuracy'))

        if seven_day_accuracy['avg_accuracy'] is None:
            return Response({
                'success': False,
                'message': 'No accuracy data found for the last 7 days.'
            }, status=status.HTTP_404_NOT_FOUND)

        data = {
            'seven_day_average_accuracy': f"{seven_day_accuracy['avg_accuracy']:.2f}%",
            'start_date': start_date.date(),
            'end_date': end_date.date()
        }

        serializer = SevenDayAverageAccuracySerializer(data)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)