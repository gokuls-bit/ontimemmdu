from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection


class HealthCheckAPIView(APIView):
    """
    GET /api/v1/health/
    API Health check and database connectivity check.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        db_status = "healthy"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"

        return Response({
            "status": "healthy" if db_status == "healthy" else "degraded",
            "service": "CSE SmartRoom API",
            "version": "v1",
            "database": db_status
        })
