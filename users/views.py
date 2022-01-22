from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from .serializers import CustomUserSerializer
from .permissions import IsLoggedIn


class RegisterView(APIView):

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):

    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        user = authenticate(email=email, password=password)
        response = Response()

        if user is not None:
            refresh_token = RefreshToken.for_user(user)
            response.set_cookie(
                key=settings.SIMPLE_JWT['COOKIE_KEY'],
                value=str(user.id),
                expires=settings.SIMPLE_JWT['COOKIE_EXPIRES'],
                secure=settings.SIMPLE_JWT['COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['COOKIE_SAMESITE']
            )
            request.session['access_token'] = str(refresh_token.access_token)
            response.data = {
                "Message": "Login successful!"
            }
            return response


class UserView(APIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):
        return JsonResponse({"Message": "Looks like you're logged in"})


class LogoutView(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('anilite_cookie')
        if request.session.get('access_token') is not None:
            del request.session['access_token']
        response.data = {"Message": "Logged out successfully"}
        return response
