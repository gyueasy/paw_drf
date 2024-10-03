from django.conf import settings
from django.core.exceptions import PermissionDenied

class IPCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            path = request.path
            if any(path.startswith(p) for p in settings.IP_CHECK_PATHS):
                user_ip = self.get_client_ip(request)
                if user_ip not in settings.ALLOWED_IPS and user_ip != request.get_host().split(':')[0]:
                    raise PermissionDenied

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip