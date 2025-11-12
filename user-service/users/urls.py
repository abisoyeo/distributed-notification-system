from django.urls import path
from .views import (
    UserCreateView,
    UserRetrieveView,
    PreferencesRetrieveUpdateView,
    PushTokenUpdateView,
)
from .auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # POST /api/v1/users/ - Create user (removed /register/)
    path('', UserCreateView.as_view(), name='user-create'),
    
    # POST /api/v1/users/login - User login
    path('login', MyTokenObtainPairView.as_view(), name='user-login'),
    
    # POST /api/v1/users/refresh - Refresh token
    path('refresh', TokenRefreshView.as_view(), name='user-refresh'),

    # GET /api/v1/users/:user_id/ - Get user by ID
    path('<uuid:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),

    # GET & PATCH /api/v1/users/:user_id/preferences - Get/Update preferences (removed trailing slash)
    path('<uuid:user_id>/preferences', PreferencesRetrieveUpdateView.as_view(), name='user-preferences'),

    # PATCH /api/v1/users/:user_id/push_token - Update push token (changed from POST push-tokens)
    path('<uuid:user_id>/push_token', PushTokenUpdateView.as_view(), name='user-push-token'),
]