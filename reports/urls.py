from django.urls import path
from . import views

urlpatterns = [
    #보고서 생성
    path('capture-and-analyze-chart/', views.capture_and_analyze_chart, name='capture_and_analyze_chart'),
    path('crawl-and-analyze-news/', views.crawl_and_analyze_news, name='crawl_and_analyze_news'),
    path('create-main-report/', views.create_main_report, name='create_main_report'),
    path('calculate-accuracy/', views.calculate_accuracy, name='calculate_accuracy'),
    path('retrospective-report/', views.create_and_analyze_retrospective_report, name='create_and_analyze_retrospective_report'),
    #보고서 조회
    path('chart-report/<int:pk>/', views.ChartReportDetailAPIView.as_view(), name='chart_report_detail'),
    path('news-report/<int:pk>/', views.NewsReportDetailAPIView.as_view(), name='news_report_detail'),
    path('report-weights/<int:pk>/', views.ReportWeightsDetailAPIView.as_view(), name='report_weights_detail'),
    path('main-report/<int:pk>/', views.MainReportDetailAPIView.as_view(), name='main_report_detail'),
    path('main-reports/', views.MainReportListAPIView.as_view(), name='main_report_list'),
]