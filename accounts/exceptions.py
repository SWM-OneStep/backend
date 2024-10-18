from rest_framework import exceptions, status


class LoginException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "device type and token is required"
    default_code = "error"

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
        if code is not None:
            self.default_code = code
        super().__init__(self.detail, self.default_code)
