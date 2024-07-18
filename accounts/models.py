from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class TimeStamp(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimeStamp):

    class SocialProvider(models.TextChoices):
        GOOGLE = "GOOGLE"
        KAKAO = "KAKAO"
        NAVER = "NAVER"

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password = models.CharField(_("password"), max_length=128, null=True)
    social_provider = models.CharField(
        max_length=30, choices=SocialProvider.choices, default=SocialProvider.GOOGLE
    )


class Device(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
