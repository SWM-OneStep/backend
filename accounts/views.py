from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import *
from accounts.serializers import *
from drf_yasg.utils import swagger_auto_schema
import jwt
import os
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


class LoginView(APIView):

    @swagger_auto_schema(
        request_body=LoginRequestSerializer,
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user = User.objects.create_user(email)
            serializer.validated_data.update({"id": user.id})
            payload_serializer = LoginPayloadSerializer(data=serializer.validated_data)
            if payload_serializer.is_valid(raise_exception=True):
                token = jwt.encode(
                    payload=payload_serializer.validated_data, key=JWT_SECRET_KEY
                )
                return Response(status=status.HTTP_200_OK, data={"token": token})
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"msg": "잘못된 접근입니다."}
        )
