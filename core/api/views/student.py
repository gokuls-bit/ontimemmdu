from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.api.throttles import StudentAnonRateThrottle
from core.api.serializers import StudentQuerySerializer, StudentScheduleQuerySerializer
from core.services.timetable.student_schedule import get_current_class, get_next_class, get_day_schedule
from core.services.timetable.timetable_state import get_student_timetable_state


class StudentCurrentClassAPIView(APIView):
    """
    GET /api/v1/student/current-class/
    Determines what a student should be attending right NOW.
    Calls Module 3: get_current_class()
    """
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = StudentQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sem = serializer.validated_data['semester']
        sec = serializer.validated_data['section']
        grp = serializer.validated_data.get('group')

        data = get_current_class(semester_val=sem, section_val=sec, group_val=grp)
        return Response({"success": True, "data": data})


class StudentNextClassAPIView(APIView):
    """
    GET /api/v1/student/next-class/
    Determines what class a student must attend NEXT today.
    Calls Module 3: get_next_class()
    """
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = StudentQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sem = serializer.validated_data['semester']
        sec = serializer.validated_data['section']
        grp = serializer.validated_data.get('group')

        data = get_next_class(semester_val=sem, section_val=sec, group_val=grp)
        return Response({"success": True, "data": data})


class StudentStateAPIView(APIView):
    """
    GET /api/v1/student/state/
    Primary consolidated student state endpoint for Module 6.
    Calls Module 3: get_student_timetable_state()
    """
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = StudentQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sem = serializer.validated_data['semester']
        sec = serializer.validated_data['section']
        grp = serializer.validated_data.get('group')

        data = get_student_timetable_state(semester_val=sem, section_val=sec, group_val=grp)
        return Response({"success": True, "data": data})


class StudentScheduleAPIView(APIView):
    """
    GET /api/v1/student/schedule/
    Returns complete ordered day schedule for student.
    Calls Module 3: get_day_schedule()
    """
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = StudentScheduleQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        sem = serializer.validated_data['semester']
        sec = serializer.validated_data['section']
        grp = serializer.validated_data.get('group')
        day = serializer.validated_data.get('day')
        order = serializer.validated_data.get('orientation') or serializer.validated_data.get('order') or 'asc'

        schedule_data = get_day_schedule(semester_val=sem, section_val=sec, group_val=grp, day_val=day, order=order)
        return Response({
            "success": True,
            "data": {
                "day": day or "Today",
                "order": order,
                "schedule": schedule_data
            }
        })
