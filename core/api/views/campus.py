from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.api.throttles import StudentAnonRateThrottle
from core.services.location import get_campus_occupancy_state, get_location_intelligence_state


class CampusOccupancyAPIView(APIView):
    """GET /api/v1/campus/occupancy/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        data = get_campus_occupancy_state()
        return Response(data)


class LocationIntelligenceStateAPIView(APIView):
    """GET /api/v1/campus/intelligence/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        room = request.query_params.get('room')
        teacher = request.query_params.get('teacher')
        data = get_location_intelligence_state(room_val=room, teacher_val=teacher)
        return Response(data)
