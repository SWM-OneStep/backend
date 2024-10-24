from rest_framework_simplejwt.tokens import RefreshToken


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user, device_token):
        token = super().for_user(user)
        token["device"] = device_token
        return token

    @classmethod
    def for_user_without_device(cls, user):
        token = super().for_user(user)
        return token
