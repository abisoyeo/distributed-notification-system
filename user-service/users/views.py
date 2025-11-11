from django.shortcuts import render
from .models import User, PushToken, NotificationPreferences
from .serializers import UserSerializer, PushTokenSerializer, NotificationPreferenceSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .auth_views import MyTokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404

class UserCreateView(generics.CreateAPIView):

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        user_data = {
            'user_id': serializer.data['id'],
            'email': serializer.data['email'],
        }


        return Response({
            "success": True,
            "message": "User registered successfully",
            "data": user_data,
            "error": None,
            "meta": {
                "total": 1,
                "limit": 1,
                "page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }, status=status.HTTP_201_CREATED, headers=headers)
        
# Create your views here.


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PreferencesRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs['user_id']
        user  = get_object_or_404(User, id=user_id)
        preferences, created = NotificationPreferences.objects.get_or_create(user=user)
        return preferences

class PushTokenCreateView(generics.CreateAPIView):
    queryset = PushToken.objects.all()
    serializer_class = PushTokenSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        serializer.save(user=user)
