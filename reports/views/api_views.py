import logging
from rest_framework import generics
from django.db.models import Avg
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import AllowAny
from ..models import ChartReport, NewsReport, MainReport, ReportWeights, Accuracy
from ..services import ReportService
from ..serializers import SevenDayAverageAccuracySerializer, ChartReportSerializer, NewsReportSerializer, ReportWeightsSerializer, MainReportSerializer, MainReportListSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

report_service = ReportService()

class ChartReportDetailAPIView(generics.RetrieveAPIView):
    queryset = ChartReport.objects.all()
    serializer_class = ChartReportSerializer

class NewsReportDetailAPIView(generics.RetrieveAPIView):
    queryset = NewsReport.objects.all()
    serializer_class = NewsReportSerializer

class ReportWeightsDetailAPIView(generics.RetrieveAPIView):
    queryset = ReportWeights.objects.all()
    serializer_class = ReportWeightsSerializer

class MainReportDetailAPIView(generics.RetrieveAPIView):
    queryset = MainReport.objects.all()
    serializer_class = MainReportSerializer

    def get_queryset(self):
        return MainReport.objects.all().select_related('chart_report', 'news_report', 'weights')
    
class MainReportListAPIView(generics.ListAPIView):
    serializer_class = MainReportListSerializer

    def get_queryset(self):
        latest_report = report_service.get_latest_main_report()
        if latest_report:
            # 최신 리포트부터 최대 10개의 리포트를 가져옵니다.
            queryset = MainReport.objects.filter(id__lte=latest_report.id).order_by('-created_at')[:10]
            # select_related를 사용하여 관련 객체들을 함께 로드합니다.
            return queryset.select_related('chart_report', 'news_report', 'weights')
        return MainReport.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            latest_accuracy = Accuracy.objects.latest('calculated_at')
            context['average_accuracy'] = f"{latest_accuracy.average_accuracy:.2f}%"
        except Accuracy.DoesNotExist:
            context['average_accuracy'] = None
        return context
    
class SevenDayAverageAccuracyAPIView(generics.RetrieveAPIView):
    serializer_class = SevenDayAverageAccuracySerializer
    permission_classes = [AllowAny]

    def get_object(self):
        cache_key = "seven_day_average_accuracy"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        seven_day_accuracy = Accuracy.objects.filter(
            calculated_at__range=(start_date, end_date)
        ).aggregate(avg_accuracy=Avg('average_accuracy'))

        result = {
            'seven_day_average_accuracy': f"{seven_day_accuracy['avg_accuracy']:.2f}%" if seven_day_accuracy['avg_accuracy'] else None,
            'start_date': start_date.date(),
            'end_date': end_date.date()
        }

        # 캐시에 결과 저장 (예: 1시간 동안)
        cache.set(cache_key, result, 3600)

        return result   