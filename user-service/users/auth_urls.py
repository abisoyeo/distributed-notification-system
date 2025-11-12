from django.urls import path
from .auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login', MyTokenObtainPairView.as_view(), name='auth-login'),
    path('refresh', TokenRefreshView.as_view(), name='auth-refresh'),
]