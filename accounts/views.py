from datetime import timedelta

import jwt
import sentry_sdk
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from fcm_django.models import FCMDevice
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import LoginException
from accounts.serializers import UserSerializer
from accounts.tokens import CustomRefreshToken

User = get_user_model()


JWT_SECRET_KEY = settings.SECRETS.get("JWT_SECRET_KEY")
GOOGLE_ANDROID_CLIENT_ID = settings.SECRETS.get("GCID")
GOOGLE_IOS_CLIENT_ID = settings.SECRETS.get("GOOGLE_IOS_CLIENT_ID")


class GoogleLogin(APIView):
    """
    request : token, device_token, type(0 : android, 1 : ios)
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            device_type, token, device_token = self.validate_request(request)
            idinfo = self.verify_token(device_type, token)
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                user = User.get_or_create_user(email)
                refresh = self.handle_device_token(user, device_token)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def validate_request(self, request):
        device_type = request.data.get("type", None)
        token = request.data.get("token")
        device_token = request.data.get("device_token", None)
        if not token or device_type is None:
            raise LoginException()
        if device_type == 0 and not device_token:
            raise LoginException("Device token is required for android login")
        return device_type, token, device_token

    def verify_token(self, device_type, token):
        if device_type == 0:  # Android
            return id_token.verify_oauth2_token(
                token,
                requests.Request(),
                audience=GOOGLE_ANDROID_CLIENT_ID,
            )
        elif device_type == 1:  # iOS
            return id_token.verify_oauth2_token(
                token, requests.Request(), audience=GOOGLE_IOS_CLIENT_ID
            )
        else:
            raise LoginException("Invalid device type")

    def handle_device_token(self, user, device_token):
        if device_token:
            FCMDevice.objects.get_or_create(
                user=user, registration_id=device_token
            )
            return CustomRefreshToken.for_user(user, device_token)
        else:
            return CustomRefreshToken.for_user_without_device(user)


class AppleLogin(APIView):
    """
    request : token, device_token, type(0 : android, 1 : ios)
    """

    ACCESS_TOKEN_URL = "https://appleid.apple.com/auth/token"
    APPLE_APP_ID = settings.SECRETS.get("APPLE_APP_ID")
    APPLE_SERVICE_ID = settings.SECRETS.get("APPLE_SERVICE_ID")
    APPLE_CERTICATE_FILE = settings.SECRETS.get("APPLE_CERTICATE_FILE")
    APPLE_KEY = settings.SECRETS.get("APPLE_KEY")
    APPLE_KEY_ID = settings.SECRETS.get("APPLE_KEY_ID")
    APPLE_PUBLIC_KEYS_URL = "https://appleid.apple.com/auth/keys"

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            device_type, token, device_token = self.validate_request(request)
            idinfo = self.verify_token(device_type, token)
            if "accounts.google.com" in idinfo["iss"]:
                email = idinfo["email"]
                user = User.get_or_create_user(email)
                refresh = self.handle_device_token(user, device_token)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def verify_token(self, access_token):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """

        client_id, client_secret = self.get_key_and_secret()

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": access_token,
            "grant_type": "refresh_token",
        }
        try:
            response = requests.post(
                AppleLogin.ACCESS_TOKEN_URL, data=data, headers=headers
            )
            response_dict = response.json()
            id_token = response_dict.get("id_token", None)

            if id_token:
                decoded_user_info = self.verify_apple_token(id_token)
                return decoded_user_info
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(e)

        raise LoginException("Invalid token")

    def verify_apple_token(self, token):
        # Fetch Apple's public keys
        response = requests.get(AppleLogin.APPLE_PUBLIC_KEYS_URL)
        if response.status_code != 200:
            raise LoginException("Unable to fetch Apple's public keys")
        apple_public_keys = response.json()["keys"]

        # Decode the token header to get the key ID
        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]

        # Find the corresponding public key
        key = next((k for k in apple_public_keys if k["kid"] == kid), None)
        if key is None:
            raise LoginException("Invalid token")

        # Construct the public key
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)

        # Verify the token
        try:
            idinfo = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=AppleLogin.APPLE_SERVICE_ID,
                issuer="https://appleid.apple.com",
            )
        except jwt.ExpiredSignatureError:
            raise LoginException("Token has expired")
        except jwt.InvalidTokenError:
            raise LoginException("Invalid token")

        return idinfo

    def get_key_and_secret(self):
        headers = {"alg": "ES256", "kid": AppleLogin.APPLE_KEY_ID}

        payload = {
            "iss": AppleLogin.APPLE_KEY,
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(days=1),
            "aud": "https://appleid.apple.com",
            "sub": AppleLogin.APPLE_SERVICE_ID,
        }

        client_secret = jwt.encode(
            payload,
            AppleLogin.APPLE_CERTICATE_FILE,
            algorithm="ES256",
            headers=headers,
        ).decode("utf-8")

        return AppleLogin.APPLE_SERVICE_ID, client_secret

    def validate_request(self, request):
        device_type = request.data.get("type", None)
        token = request.data.get("token")
        device_token = request.data.get("device_token", None)
        if not token or device_type is None:
            raise LoginException()
        if device_type == 0 and not device_token:
            raise LoginException("Device token is required for android login")
        return device_type, token, device_token

    def handle_device_token(self, user, device_token):
        if device_token:
            FCMDevice.objects.get_or_create(
                user=user, registration_id=device_token
            )
            return CustomRefreshToken.for_user(user, device_token)
        else:
            return CustomRefreshToken.for_user_without_device(user)


class UserRetrieveView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sentry_sdk.set_user(
                {
                    "id": request.user.id,
                    "username": request.user.username,
                }
            )
            user = User.objects.get(username=request.user.username)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request):
        """
        입력 : is_subscribe (Boolean), is_premium (Boolean)
        """
        try:
            user = request.user
            sentry_sdk.set_user(
                {
                    "id": request.user.id,
                    "username": request.user.username,
                }
            )
            if request.data.get("is_premium"):
                user.is_premium = request.data.get("is_premium")
            if request.data.get("is_subscribed"):
                user.is_subscribed = request.data.get("is_subscribed")
            user.save()
            serializer = UserSerializer(user)
            sentry_sdk.capture_message("User updated", level="info")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AndroidClientView(APIView):
    def get(self, request):
        try:
            return Response(
                {"android_client_id": GOOGLE_ANDROID_CLIENT_ID},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Android client id not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IOSClientView(APIView):
    def get(self, request):
        try:
            return Response(
                {"ios_client_id": GOOGLE_IOS_CLIENT_ID},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "IOS client id not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
