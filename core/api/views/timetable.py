from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.services.timetable.downloads import serve_timetable_download


class TimetableDownloadAPIView(APIView):
    """
    GET /api/v1/timetable/<semester>/<fmt>/
    Proxies secure timetable file downloads (3rd, 4th, 5th semester Excel & JSON).
    """
    permission_classes = [AllowAny]

    def get(self, request, semester, fmt):
        return serve_timetable_download(request, semester, fmt)
