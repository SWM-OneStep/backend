import logging
# from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response

logger = logging.getLogger(__name__)
class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)
        state_code= getattr(response, 'status_code', None)
        request = (f"Request : {request.path}, {request.method}, {state_code}, {response.data}")
        if state_code >= 500:
            logger.critical(request)
        elif state_code >= 400:
            logger.error(request)
        elif state_code >= 300:
            logger.warning(request)
        elif state_code >= 200:
            logger.info(request)
        else: # state_code < 200
            logger.debug(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response