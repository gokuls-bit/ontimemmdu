from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.api.throttles import StudentAnonRateThrottle
from core.api.serializers import TeacherSearchQuerySerializer
from core.services.location import (
    get_teacher_current_location, search_teachers, get_teacher_day_schedule,
    get_teacher_next_class, get_all_teacher_statuses
)


class TeacherSearchAPIView(APIView):
    """GET /api/v1/teachers/search/?q=Sharma"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = TeacherSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        q = serializer.validated_data['q']
        data = search_teachers(query=q)
        return Response(data)


class TeacherLocationAPIView(APIView):
    """GET /api/v1/teachers/<teacher>/location/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, teacher):
        data = get_teacher_current_location(teacher_val=teacher)
        return Response(data)


class TeacherNextClassAPIView(APIView):
    """GET /api/v1/teachers/<teacher>/next-class/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, teacher):
        data = get_teacher_next_class(teacher_val=teacher)
        return Response(data if data is not None else {})


class TeacherScheduleAPIView(APIView):
    """GET /api/v1/teachers/<teacher>/schedule/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, teacher):
        day = request.query_params.get('day')
        data = get_teacher_day_schedule(teacher_val=teacher, day_val=day)
        return Response({
            "teacher": teacher,
            "day": day or "Today",
            "schedule": data
        })


class AllTeacherStatusAPIView(APIView):
    """GET /api/v1/teachers/status/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        data = get_all_teacher_statuses()
        return Response(data)
