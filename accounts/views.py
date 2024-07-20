from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import *
from accounts.serializers import *
import jwt
import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


JWT_SECRET_KEY = settings.SECRETS.get("JWT_SECRET_KEY")
GOOGLE_CLIENT_ID = settings.SECRETS.get("GCID")


class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, World!"})


class GoogleLogin(APIView):
    google_client_id = settings.SECRETS.get("GCID")

    def post(self, request):
        token = request.data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_CLIENT_ID
            )
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                name = idinfo.get("name", "")
                user, _ = User.objects.get_or_create(username=email, password="")
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
