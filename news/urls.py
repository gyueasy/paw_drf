from django.urls import path
from .views import NewsListView, NewsItemUpdateView

urlpatterns = [
    path('', NewsListView.as_view(), name='news-list'),
    path('<int:id>/update/', NewsItemUpdateView.as_view(), name='news-item-update'),
]
