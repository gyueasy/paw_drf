from django.urls import path
from . import views

urlpatterns = [
    path('capture-and-analyze-chart/', views.capture_and_analyze_chart, name='capture_and_analyze_chart'),
]