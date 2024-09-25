from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import LoginException
from accounts.models import Device
from accounts.serializers import UserSerializer
from accounts.tokens import CustomRefreshToken

User = get_user_model()


JWT_SECRET_KEY = settings.SECRETS.get("JWT_SECRET_KEY")
GOOGLE_CLIENT_ID = settings.SECRETS.get("GCID")


class GoogleLogin(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        device_token = request.data.get("device_token")
        if not device_token or not token:
            raise LoginException()
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_CLIENT_ID
            )
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                user = User.get_or_create_user(email)
                Device.objects.get_or_create(user_id=user, token=device_token)
                refresh = CustomRefreshToken.for_user(user, device_token)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class UserRetrieveView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        """
        입력 : is_subscribe (Boolean)
        """
        user = User.objects.get(username=request.user.username)
        user.is_subscribed = request.data.get("is_subscribed")
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AndroidClientView(APIView):
    def get(self, request):
        ANDROID_CLIENT_ID = settings.SECRETS.get("ANDROID_CLIENT_ID")
        return Response(
            {"android_client_id": ANDROID_CLIENT_ID}, status=status.HTTP_200_OK
        )
