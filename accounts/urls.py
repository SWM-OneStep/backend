from django.contrib import admin
from django.urls import path, include
from accounts.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("login/google/", GoogleLogin.as_view(), name="google_login"),
    path("test/", TestView.as_view(), name="test"),
    path("user/", UserRetrieveView.as_view(), name="user"),
]
