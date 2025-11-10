from django.shortcuts import render
from .models import User, PushToken
from .serializers import UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response

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
