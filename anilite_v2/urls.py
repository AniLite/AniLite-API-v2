from django.contrib import admin
from django.urls import path, include
from animu.views import test

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('animu.api.urls')),
    path('user/', include('users.urls')),
    path('test', test)
]
