from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken
from .models import CustomUser


class IsLoggedIn(permissions.BasePermission):

    def has_permission(self, request, view):
        user_id = request.COOKIES.get('anilite_cookie', None)
        token = request.session.get('access_token')
        if user_id is None:
            return False
        token_object = AccessToken(token)
        return int(user_id) == int(token_object['user_id'])


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        user_id = request.COOKIES.get('anilite_cookie', None)
        if user_id is not None:
            user = CustomUser.objects.get(id=user_id)
            return user.is_superuser
        return False
