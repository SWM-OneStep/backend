from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import *
from accounts.serializers import *
import jwt
import os
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth.models import User


load_dotenv()


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")


class GoogleLogin(APIView):
    def post(self, request):
        token = request.data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), GOOGLE_CLIENT_ID
            )
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                name = idinfo.get("name", "")
                user, _ = User.objects.get_or_create(
                    email=email,
                    name=name,
                )
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
