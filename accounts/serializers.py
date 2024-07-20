from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os
from django.conf import settings


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    google_client_id = settings.SECRETS.get("GCID")

    @classmethod
    def get_token(self, user):
        token = super().get_token(user)
        token["aud"] = self.google_client_id
        return token


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="email")
    provider = serializers.CharField(help_text="provider")
    access_token = serializers.CharField(help_text="access token")

    class Meta:
        fields = ["email", "provider", "access_token"]


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="jwt token")


class LoginPayloadSerializer(LoginRequestSerializer):
    id = serializers.IntegerField(help_text="user id")
    current_time = serializers.CharField()

    class Meta:
        fields = LoginRequestSerializer.Meta.fields + ["id"]

    def to_internal_value(self, data):
        data.update({"current_time": datetime.now().isoformat()})
        return super().to_internal_value(data)

    def is_valid(self, *, raise_exception=False):

        return super().is_valid(raise_exception=raise_exception)
