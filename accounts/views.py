from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from accounts.models import *
from accounts.serializers import *
import os
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializers import *
from accounts.tokens import CustomRefreshToken


User = get_user_model()


load_dotenv()


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GCID")


class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, World!"})


class GoogleLogin(APIView):
    google_client_id = os.environ.get("GCID")

    def post(self, request):
        token = request.data.get("token")
        device_token = request.data.get("deviceToken")
        if not device_token or not token:
            raise Exception("device token and token is required")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_CLIENT_ID
            )
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                user, _ = User.objects.get_or_create(username=email, password="")
                Device.objects.get_or_create(user_id=user, token=device_token)
                refresh = CustomRefreshToken.for_user(user, device_token)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)
