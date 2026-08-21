import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class CORSMiddleware:
    """
    Lightweight CORS middleware for handling API cross-origin requests.
    Supports localhost origins in development and CORS_ALLOWED_ORIGINS in production.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS" and request.path.startswith("/api/"):
            response = self.get_response(request)
            response.status_code = 200
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response

        response = self.get_response(request)

        if request.path.startswith("/api/"):
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', ['http://localhost:3000', 'http://127.0.0.1:3000'])
            origin = request.headers.get('Origin')
            if settings.DEBUG:
                response["Access-Control-Allow-Origin"] = origin if origin else "*"
            elif origin in allowed_origins:
                response["Access-Control-Allow-Origin"] = origin

            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"

        return response


class APILoggingMiddleware:
    """
    Logs API endpoint access, HTTP status, and duration without leaking sensitive parameters.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        start_time = time.time()
        response = self.get_response(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"API {request.method} {request.path} -> {response.status_code} ({duration_ms}ms)"
        )
        return response
