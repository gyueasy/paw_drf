from .chart_views import capture_and_analyze_chart
from .news_views import crawl_and_analyze_news
from .main_report_views import create_main_report

from .retrospective_views import create_and_analyze_retrospective_report
from .accuracy_views import calculate_accuracy
from .api_views import SevenDayAverageAccuracyAPIView, MainReportDetailAPIView, MainReportListAPIView, ReportWeightsDetailAPIView, ChartReportDetailAPIView, NewsReportDetailAPIView