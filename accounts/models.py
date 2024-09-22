from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.utils import (
    render_to_string_html,
    send_email,
)


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
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."  # noqa : E501
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password = models.CharField(_("password"), max_length=128, null=True)
    social_provider = models.CharField(
        max_length=30,
        choices=SocialProvider.choices,
        default=SocialProvider.GOOGLE,
    )


class Device(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class PatchNote(models.Model):
    title = models.CharField(max_length=255)
    html_file = models.FileField(upload_to="patch_note/")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    email_sent = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 모든 사용자에게 이메일 보내기
        self.send_email_to_all_users()

    def send_email_to_all_users(self):
        # 모든 사용자에게 이메일 보내기
        user_email_list = User.objects.filter(
            deleted_at__isnull=True, is_staff=False
        ).values_list("username", flat=True)
        subject = f"OneStep's New Patch Note: {self.title}"

        message = render_to_string_html("welcome_email.html")
        send_email(
            to_email_address=list(user_email_list),
            subject=subject,
            message=message,
        )
