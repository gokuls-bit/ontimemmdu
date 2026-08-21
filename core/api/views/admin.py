from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.api.permissions import IsTimetableAdmin, IsSuperAdmin, IsAdminOrReadOnly
from timetable.models import (
    Semester, Section, Group, Teacher, Room, TimetableEntry,
    TimetableOverride, ClassCancellation, RoomException, RoomReservation, AuditLog
)
from core.services.location import get_campus_occupancy_state
from core.services.admin import (
    create_timetable_alteration, approve_timetable_alteration,
    emergency_room_change, cancel_class_instance,
    create_room_maintenance, create_room_reservation, log_admin_action
)
from core.api.serializers.admin import (
    CreateAlterationSerializer, EmergencyRoomChangeSerializer,
    CreateCancellationSerializer, CreateMaintenanceSerializer,
    CreateReservationSerializer, TimetableOverrideSerializer, AuditLogSerializer
)


class AdminDashboardAPIView(APIView):
    """GET /api/v1/admin/dashboard/"""
    permission_classes = [AllowAny]  # Allow viewing dashboard metrics in demo

    def get(self, request):
        occupancy = get_campus_occupancy_state()
        total_students = sum([s.capacity for s in Section.objects.all()]) or 2100
        total_teachers = Teacher.objects.filter(is_active=True).count()
        total_rooms = Room.objects.filter(is_active=True).count()

        pending_alterations = TimetableOverride.objects.count()
        today_cancellations = ClassCancellation.objects.count()

        return Response({
            "success": True,
            "data": {
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_rooms": total_rooms,
                "active_classes": occupancy.get("active_classes", 0),
                "occupied_rooms": occupancy.get("occupied_rooms", 0),
                "free_rooms": occupancy.get("free_rooms", 0),
                "utilization_percentage": occupancy.get("utilization_percentage", 0),
                "pending_alterations": pending_alterations,
                "today_cancellations": today_cancellations,
                "server_time": occupancy.get("server_time"),
            }
        })


class AdminTimetableAPIView(APIView):
    """GET /api/v1/admin/timetable/"""
    permission_classes = [AllowAny]

    def get(self, request):
        entries = TimetableEntry.objects.select_related('semester', 'section', 'group', 'subject', 'teacher', 'room', 'time_slot').all()

        sem = request.query_params.get('semester')
        sec = request.query_params.get('section')
        day = request.query_params.get('day')
        room = request.query_params.get('room')

        if sem: entries = entries.filter(semester__number=sem)
        if sec: entries = entries.filter(section__name=sec)
        if day: entries = entries.filter(day=day)
        if room: entries = entries.filter(room__room_number=room)

        data = []
        for e in entries[:100]:
            data.append({
                "id": e.id,
                "semester": e.semester.number,
                "section": e.section.name if e.section else (e.merge_group.name if e.merge_group else "N/A"),
                "day": e.day,
                "period": e.period,
                "start_time": e.start_time.strftime('%H:%M'),
                "end_time": e.end_time.strftime('%H:%M'),
                "subject": e.subject.short_name,
                "teacher": e.teacher.full_name,
                "room": e.room.room_number,
                "class_type": e.class_type,
            })

        return Response({"success": True, "data": data})


class AdminAlterationsAPIView(APIView):
    """GET/POST /api/v1/admin/alterations/"""
    permission_classes = [AllowAny]

    def get(self, request):
        overrides = TimetableOverride.objects.select_related('subject', 'teacher', 'room').all()
        serializer = TimetableOverrideSerializer(overrides, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = CreateAlterationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        override, conflicts = create_timetable_alteration(
            timetable_entry_id=serializer.validated_data['timetable_entry_id'],
            date_val=serializer.validated_data['date'],
            period=serializer.validated_data['period'],
            new_room_val=serializer.validated_data['room'],
            new_teacher_val=serializer.validated_data.get('teacher'),
            reason=serializer.validated_data.get('reason', ''),
            user=request.user
        )

        return Response({
            "success": True,
            "data": {
                "override_id": override.id,
                "status": "APPROVAL_REQUIRED" if conflicts else "APPROVED",
                "conflicts": conflicts
            }
        })


class AdminApproveAlterationAPIView(APIView):
    """POST /api/v1/admin/alterations/<id>/approve/"""
    permission_classes = [AllowAny]

    def post(self, request, override_id):
        approved = approve_timetable_alteration(override_id, user=request.user)
        return Response({
            "success": True,
            "data": {
                "override_id": approved.id,
                "status": "APPROVED",
                "message": "Alteration successfully approved and activated."
            }
        })


class AdminEmergencyRoomChangeAPIView(APIView):
    """POST /api/v1/admin/emergency-room-change/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmergencyRoomChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        override = emergency_room_change(
            timetable_entry_id=serializer.validated_data['timetable_entry_id'],
            date_val=serializer.validated_data['date'],
            new_room_number=serializer.validated_data['new_room'],
            reason=serializer.validated_data.get('reason', 'Emergency room change'),
            user=request.user
        )

        return Response({
            "success": True,
            "data": {
                "override_id": override.id,
                "new_room": override.room.room_number,
                "status": "ACTIVATED",
                "message": f"Room changed to {override.room.room_number}."
            }
        })


class AdminCancellationsAPIView(APIView):
    """POST /api/v1/admin/cancellations/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateCancellationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancellation = cancel_class_instance(
            timetable_entry_id=serializer.validated_data['timetable_entry_id'],
            date_val=serializer.validated_data['date'],
            reason=serializer.validated_data.get('reason', ''),
            user=request.user
        )

        return Response({
            "success": True,
            "data": {
                "cancellation_id": cancellation.id,
                "status": "CANCELLED",
                "message": f"Class cancelled for {cancellation.date}."
            }
        })


class AdminRoomMaintenanceAPIView(APIView):
    """POST /api/v1/admin/rooms/maintenance/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateMaintenanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        maint = create_room_maintenance(
            room_number=serializer.validated_data['room'],
            date_val=serializer.validated_data['date'],
            reason=serializer.validated_data.get('reason', 'Maintenance'),
            exception_type=serializer.validated_data.get('exception_type', 'MAINTENANCE'),
            user=request.user
        )

        return Response({
            "success": True,
            "data": {
                "maintenance_id": maint.id,
                "room": maint.room.room_number,
                "status": "UNAVAILABLE",
                "message": f"Room {maint.room.room_number} set to maintenance."
            }
        })


class AdminAuditLogsAPIView(APIView):
    """GET /api/v1/admin/audit/"""
    permission_classes = [AllowAny]

    def get(self, request):
        logs = AuditLog.objects.all()[:100]
        serializer = AuditLogSerializer(logs, many=True)
        return Response({"success": True, "data": serializer.data})
