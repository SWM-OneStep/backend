import jwt
import sentry_sdk
from django.conf import settings
from django.contrib.auth import get_user_model
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

    APPLE_SERVICE_ID = settings.SECRETS.get("APPLE_SERVICE_ID")
    APPLE_PUBLIC_KEYS_URL = "https://appleid.apple.com/auth/keys"

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            device_type, token, device_token = self.validate_request(request)
            # verify apple token and get email
            email = self.verify_token(device_type, token)
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

    def verify_token(self, token):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        # Apple 공개 키 가져오기
        response = requests.get(AppleLogin.APPLE_PUBLIC_KEYS_URL)
        if response.status_code != 200:
            raise LoginException("Unable to fetch Apple's public keys")
        apple_public_keys = response.json()["keys"]
        # JWT 디코드 및 서명 검증
        header = jwt.get_unverified_header(token)

        # 헤더의 'kid'와 일치하는 Apple 공개 키 선택
        public_key = next(
            key
            for key in apple_public_keys["keys"]
            if key["kid"] == header["kid"]
        )

        if public_key is None:
            raise LoginException("Invalid token")

        # Verify the token
        try:
            decoded_token = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],  # Apple의 서명 알고리즘
                audience=AppleLogin.APPLE_SERVICE_ID,
                issuer="https://appleid.apple.com",
            )
            return decoded_token.get("email")
        except jwt.ExpiredSignatureError:
            sentry_sdk.capture_exception(jwt.ExpiredSignatureError)
            raise LoginException("Token has expired")
        except jwt.InvalidTokenError:
            sentry_sdk.capture_exception(jwt.ExpiredSignatureError)
            raise LoginException("Invalid token")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise LoginException("An unexpected error occurred")

    def validate_request(self, request):
        device_type = request.data.get("type", None)
        token = request.data.get("token")
        device_token = request.data.get("device_token", None)
        if not token or device_type is None:
            raise LoginException()
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
            user = User.objects.get(
                username=request.user.username, deleted_at__isnull=True
            )
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

    def delete(self, request):
        try:
            user = request.user
            user = User.delete_user(instance=user)
            return Response(
                {"message": "User deleted"}, status=status.HTTP_200_OK
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
