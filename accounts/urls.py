from django.urls import path
from .views import GoogleLogin, CustomLogoutView, AccountView, ProfileView

urlpatterns = [
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('profile/', ProfileView.as_view(), name='profile'),
]