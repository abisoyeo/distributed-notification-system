from django.urls import path
from .views import UserCreateView
from .auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('users/<int:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
    path('users/<int:user_id>/preferences/', PreferencesRetrieveUpdateView.as_view(), name='user-preferences'),
    path('users/<int:user_id>/push-tokens/', PushTokenCreateView.as_view(), name='user-push-tokens'),
]