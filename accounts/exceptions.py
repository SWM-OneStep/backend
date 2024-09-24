from rest_framework import exceptions, status


class LoginException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "device token and token is required"
    default_code = "error"
