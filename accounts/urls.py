from django.contrib import admin
from django.urls import path, include
from accounts.views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/google/", GoogleLogin.as_view(), name="google_login"),
]
