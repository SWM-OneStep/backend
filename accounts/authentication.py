from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        user_id = validated_token.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])

        if not user_id:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise InvalidToken('User not found')
        
        if not user.is_active:
            raise InvalidToken('User is not active')

        return user
