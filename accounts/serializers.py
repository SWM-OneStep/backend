from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import Profile

User = get_user_model()


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "social_provider",
            "is_subscribed",
            "is_premium",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "user_id",
            "username",
            "age",
            "job",
            "sleep_time",
            "delay_reason",
        ]


class SwaggerProfileSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="username")
    age = serializers.CharField(help_text="age")
    job = serializers.CharField(help_text="job")
    sleep_time = serializers.CharField(help_text="sleep time")
    delay_reason = serializers.ListField(
        child=serializers.IntegerField(), help_text="delay reason"
    )

    class Meta:
        fields = ["username", "age", "job", "sleep_time", "delay_reason"]
