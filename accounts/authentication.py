from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from jwt import DecodeError, ExpiredSignatureError
import jwt


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            token_payload = jwt.decode(
                raw_token, 
                api_settings.SIGNING_KEY, 
                algorithms=[api_settings.ALGORITHM]
            )
            request.auth = token_payload
        except (InvalidToken, DecodeError, ExpiredSignatureError) as e:
            raise InvalidToken(e)

        return self.get_user(validated_token), token_payload
