from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('capture-and-analyze-chart/', views.capture_and_analyze_chart, name='capture_and_analyze_chart'),
    path('crawl-news/', views.crawl_and_analyze_news, name='crawl_news'),
    path('create_main_report/', views.create_main_report, name='create_main_report'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)