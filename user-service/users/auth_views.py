from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # add custom claims if you want
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # include some user data in the response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'full_name': getattr(self.user, 'full_name', ''),
        }
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
