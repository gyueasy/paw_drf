import logging
from rest_framework import generics
from ..models import ChartReport, NewsReport, MainReport, ReportWeights, Accuracy
from ..serializers import ChartReportSerializer, NewsReportSerializer, ReportWeightsSerializer, MainReportSerializer, MainReportListSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    queryset = MainReport.objects.all().order_by('-created_at')
    serializer_class = MainReportListSerializer

    def get_queryset(self):
        return MainReport.objects.all().select_related('chart_report', 'news_report', 'weights')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            latest_accuracy = Accuracy.objects.latest('calculated_at')
            context['average_accuracy'] = f"{latest_accuracy.average_accuracy:.2f}%"
        except Accuracy.DoesNotExist:
            context['average_accuracy'] = None
        return context