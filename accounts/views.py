import jwt
import requests
import sentry_sdk
import urllib3
from django.conf import settings
from django.contrib.auth import get_user_model
from fcm_django.models import FCMDevice
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import LoginException
from accounts.models import Profile
from accounts.serializers import ProfileSerializer, UserSerializer
from accounts.tokens import CustomRefreshToken

User = get_user_model()


JWT_SECRET_KEY = settings.SECRETS.get("JWT_SECRET_KEY")
GOOGLE_ANDROID_CLIENT_ID = settings.SECRETS.get("GCID")
GOOGLE_IOS_CLIENT_ID = settings.SECRETS.get("GOOGLE_IOS_CLIENT_ID")
DEVICE_TYPE_ANDROID = 0
DEVICE_TYPE_IOS = 1


class BaseLogin(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            device_type, token, device_token = self.validate_request(request)
            email = self.verify_token(device_type, token)
            user, is_new = User.get_or_create_user(email)
            refresh = self.handle_device_token(user, device_token)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "is_new": is_new,
                    "email": email,
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

    def handle_device_token(self, user, device_token):
        if device_token:
            FCMDevice.objects.get_or_create(
                user=user, registration_id=device_token
            )
            return CustomRefreshToken.for_user(user, device_token)
        else:
            return CustomRefreshToken.for_user_without_device(user)


class GoogleLogin(BaseLogin):
    def verify_token(self, device_type, token):
        audience = self.get_audience(device_type)
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=audience,
        )
        self.validate_issuer(idinfo)
        return idinfo["email"]

    def get_audience(self, device_type):
        if device_type == DEVICE_TYPE_ANDROID:
            return GOOGLE_ANDROID_CLIENT_ID
        elif device_type == DEVICE_TYPE_IOS:
            return GOOGLE_IOS_CLIENT_ID
        else:
            raise LoginException("Invalid device type")

    def validate_issuer(self, idinfo):
        if "accounts.google.com" not in idinfo["iss"]:
            raise LoginException("Invalid token")


class AppleLogin(BaseLogin):
    APPLE_APP_ID = settings.SECRETS.get("APPLE_APP_ID")
    APPLE_PUBLIC_KEYS_URL = "https://appleid.apple.com/auth/keys"

    def verify_token(self, device_type, identity_token):
        if device_type != DEVICE_TYPE_IOS:
            raise LoginException("Invalid device type")
        try:
            unverified_header = jwt.get_unverified_header(identity_token)
            kid = unverified_header["kid"]
            public_key = self.get_apple_public_key(kid)
            decoded_token = jwt.decode(
                identity_token,
                public_key,
                algorithms=["RS256"],
                audience=self.APPLE_APP_ID,
                issuer="https://appleid.apple.com",
            )
            email = decoded_token.get("email", None)
            return email
        except jwt.ExpiredSignatureError as e:
            sentry_sdk.capture_exception(e)
            raise LoginException("Token has expired")
        except jwt.InvalidTokenError as e:
            sentry_sdk.capture_exception(e)
            raise LoginException("Invalid token")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise LoginException(f"An unexpected error occurred: {e}")

    def get_apple_public_key(self, kid):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(self.APPLE_PUBLIC_KEYS_URL, verify=False)
        keys = response.json().get("keys", [])
        for key in keys:
            if key["kid"] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        raise ValueError("Matching key not found")


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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        - profile 정보를 조회합니다.
        - 입력 : user_id
        """
        user_id = request.user.id
        try:
            user_info = Profile.objects.get(user_id=user_id)
            serializer = ProfileSerializer(user_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        """
        - profile 정보를 입력받아서 저장합니다.
        - 입력 : username, age, job, sleep_time, wake_time, delay_reason
        """
        user_id = request.user.id
        if Profile.objects.filter(user_id=user_id).exists():
            return Response(
                {"error": "Profile already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data.copy()
        data["user_id"] = user_id
        serializer = ProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """
        - profile 정보를 입력받아서 수정합니다.
        - 입력 : username, age, job, sleep_time, wake_time, delay_reason
        - 예외 : user_id 를 수정하려는 경우에 400 에러가 발생합니다.
        """
        user_id = request.user.id
        if "user_id" in request.data:
            return Response(
                {"error": "user_id cannot be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            userInfo = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ProfileSerializer(
            context={"request": request},
            instance=userInfo,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
