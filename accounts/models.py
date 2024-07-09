from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class TimeStamp(models.Model):
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class UserSignupManager(models.Manager):

    def create_user(self, email):
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            return user


class User(TimeStamp):

    class SocialProvider(models.TextChoices):
        GOOGLE = "GOOGLE"
        KAKAO = "KAKAO"
        NAVER = "NAVER"

    email = models.EmailField(unique=True)
    signup = UserSignupManager()
    name = models.CharField(max_length=100, null=True)
    social_provider = models.CharField(
        max_length=30, choices=SocialProvider.choices, default=SocialProvider.GOOGLE
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
    


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
