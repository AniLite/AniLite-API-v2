from rest_framework import status
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.conf import settings
from .serializers import CustomUserSerializer
from .permissions import IsLoggedIn
from .models import CustomUser
from django.views.decorators.cache import cache_page
from rest_framework.decorators import permission_classes, api_view


@cache_page(30)
@permission_classes([IsLoggedIn])
@api_view(['GET'])
def cache_view(request):
    user_id = request.COOKIES.get('anilite_cookie')
    user = CustomUser.objects.get(id=user_id)
    username = user.username
    return JsonResponse({"username": username})


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

        if email is None or password is None:
            message = {"Invalid": "Email and / or password not provided."}
            return Response(message, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(email=email, password=password)

        print(user)

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
        else:
            message = {"Invalid": "User with the given credentials not found."}
            return Response(message, status=status.HTTP_404_NOT_FOUND)


class UserView(APIView):

    permission_classes = [IsLoggedIn]

    def get(self, request):
        user_id = request.COOKIES.get('anilite_cookie')
        user = CustomUser.objects.get(id=user_id)
        serializer = CustomUserSerializer(user, many=False)
        return Response(serializer.data)


class LogoutView(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('anilite_cookie')
        if request.session.get('access_token') is not None:
            del request.session['access_token']
        response.data = {"Message": "Logged out successfully"}
        return response
