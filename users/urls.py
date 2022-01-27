from django.urls import path
from .views import LoginView, LogoutView, RegisterView, UserView, cache_view

urlpatterns = [
    path('', UserView.as_view()),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view()),
    path('register', RegisterView.as_view()),
    path('cache', cache_view)
]
