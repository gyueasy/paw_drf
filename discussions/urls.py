from django.urls import path
from .views import DiscussionList, DiscussionDetail

urlpatterns = [
    path('/', DiscussionList.as_view(), name='discussion-list'),
    path('/<int:pk>/', DiscussionDetail.as_view(), name='discussion-detail'),
]