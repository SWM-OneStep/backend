from django.conf import settings

class SkipAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.SKIP_AUTHENTICATION:
            request.user = None
        response = self.get_response(request)
        return response