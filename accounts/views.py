from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer
from accounts.tokens import CustomRefreshToken

User = get_user_model()


JWT_SECRET_KEY = settings.SECRETS.get("JWT_SECRET_KEY")
GOOGLE_CLIENT_ID = settings.SECRETS.get("GCID")


class TestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, World!"})


class GoogleLogin(APIView):
    google_client_id = settings.SECRETS.get("GCID")
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        device_token = request.data.get("device_token")
        if not device_token or not token:
            raise Exception("device token and token is required")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_CLIENT_ID
            )
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                user, _ = User.objects.get_or_create(
                    username=email, password=""
                )
                refresh = CustomRefreshToken.for_user(user, device_token)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class AndroidClientView(APIView):
    def get(self, request):
        ANDROID_CLIENT_ID = settings.SECRETS.get("ANDROID_CLIENT_ID")
        return Response(
            {"android_client_id": ANDROID_CLIENT_ID}, status=status.HTTP_200_OK
        )
