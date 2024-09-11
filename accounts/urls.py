from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from accounts.views import (
    AndroidClientView,
    EmailView,
    GoogleLogin,
    TestView,
    UserRetrieveView,
)

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("login/google/", GoogleLogin.as_view(), name="google_login"),
    path("test/", TestView.as_view(), name="test"),
    path("user/", UserRetrieveView.as_view(), name="user"),
    path("android/", AndroidClientView.as_view(), name="android"),
    path("email/", EmailView.as_view(), name="email"),
]
