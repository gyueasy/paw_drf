from django.urls import path
from .views import (
    capture_and_analyze_chart,
    crawl_and_analyze_news,
    create_main_report,
    calculate_accuracy,
    create_and_analyze_retrospective_report,
    ChartReportDetailAPIView,
    NewsReportDetailAPIView,
    ReportWeightsDetailAPIView,
    MainReportDetailAPIView,
    MainReportListAPIView
)
from accounts.views import CommentView, LikeView

urlpatterns = [
    #보고서 생성
    path('chart/', capture_and_analyze_chart, name='capture_chart'),
    path('news/', crawl_and_analyze_news, name='crawl_and_analyze_news'),
    path('main/', create_main_report, name='create_main_report'),
    path('accuracy/', calculate_accuracy, name='calculate_accuracy'),
    path('retrospective/', create_and_analyze_retrospective_report, name='create_and_analyze_retrospective_report'),
    #보고서 조회
    path('chart-report/<int:pk>/', ChartReportDetailAPIView.as_view(), name='chart_detail'),
    path('news-report/<int:pk>/', NewsReportDetailAPIView.as_view(), name='news_detail'),
    path('report-weights/<int:pk>/', ReportWeightsDetailAPIView.as_view(), name='weights_detail'),
    path('main-report/<int:pk>/', MainReportDetailAPIView.as_view(), name='main_report_detail'),
    path('main-reports/', MainReportListAPIView.as_view(), name='main_report_list'),
    # 댓글 및 좋아요 (accounts app)
    path('<int:report_id>/comment/', CommentView.as_view(), name='create_comment'),
    path('comments/<int:comment_id>/', CommentView.as_view(), name='update_delete_comment'),
    path('<int:report_id>/like/', LikeView.as_view(), name='like_unlike_report'),
]