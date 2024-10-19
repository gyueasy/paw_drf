from django.urls import path
from .views import CryptoNewsView, NewsItemUpdateView

urlpatterns = [
    path('crypto-news/', CryptoNewsView.as_view(), name='crypto_news'),
    path('news-items/<int:id>/update/', NewsItemUpdateView.as_view(), name='newsitem-update'),
]
