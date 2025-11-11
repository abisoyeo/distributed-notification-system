from django.urls import path
from .views import (UserCreateView,
                    UserRetrieveView,
                    PreferencesRetrieveUpdateView,
                    PushTokenCreateView,
                    )
from .auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<uuid:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
    path('<uuid:user_id>/preferences/', PreferencesRetrieveUpdateView.as_view(), name='user-preferences'),
    path('<uuid:user_id>/push-tokens/', PushTokenCreateView.as_view(), name='user-push-tokens'),
]