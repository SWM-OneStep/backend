from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class CustomUserManager(models.Manager):

    def create_user(self, email):
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            return user


class User(models.Model):
    email = models.EmailField(unique=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
