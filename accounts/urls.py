from django.urls import path
from .views import GoogleLoginView, CustomLogoutView, AccountView, ProfileView

urlpatterns = [
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
#comments와 likers는 reports에서 관리함