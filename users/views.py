from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from .serializers import CustomUserSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)
        response = Response()

        if user is not None:
            refresh_token = RefreshToken.for_user(user)
            response.set_cookie(
                key=settings.SIMPLE_JWT['COOKIE_KEY'],
                value=str(refresh_token.access_token),
                expires=settings.SIMPLE_JWT['COOKIE_EXPIRES'],
                secure=settings.SIMPLE_JWT['COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['COOKIE_SAMESITE']
            )
            response.data = {
                "Message": "Log in successful!"
            }
            return response


# def get_user_profile(request):
#     user = request.user
#     serializer = UserSerializer(user, many=False)
#     return Response(serializer.data)


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('anilite_cookie', None)
        if token is None:
            return Response({
                "Message": "Session expired, log in again to continue"
            })
        token_obj = AccessToken(token)
        user_id = token_obj['user_id']
        user = CustomUser.objects.get(id=user_id)
        serializer = CustomUserSerializer(user, many=False)
        return Response(serializer.data)


class LogoutView(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('anilite_cookie')
        response.data = {"Message": "Logged out successfully"}
        return response
