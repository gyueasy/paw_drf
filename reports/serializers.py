from rest_framework import serializers
from .models import ChartReport, NewsReport, ReportWeights, MainReport

class ChartReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartReport
        fields = '__all__'

class NewsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsReport
        fields = '__all__'

class ReportWeightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportWeights
        fields = '__all__'

class MainReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = MainReport
        fields = '__all__'

    def get_chart_report(self, obj):
        if obj.chart_report_id:
            try:
                chart_report = ChartReport.objects.get(id=obj.chart_report_id)
                return ChartReportSerializer(chart_report).data
            except ChartReport.DoesNotExist:
                return None
        return None

    def get_news_report(self, obj):
        if obj.news_report_id:
            try:
                news_report = NewsReport.objects.get(id=obj.news_report_id)
                return NewsReportSerializer(news_report).data
            except NewsReport.DoesNotExist:
                return None
        return None

    def get_weights(self, obj):
        if obj.weights_id:
            try:
                weights = ReportWeights.objects.get(id=obj.weights_id)
                return ReportWeightsSerializer(weights).data
            except ReportWeights.DoesNotExist:
                return None
        return None
    
class MainReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainReport
        fields = ['id', 'title', 'recommendation', 'created_at']