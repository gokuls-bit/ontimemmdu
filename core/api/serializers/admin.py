from rest_framework import serializers
from timetable.models import TimetableOverride, ClassCancellation, RoomException, RoomReservation, AuditLog, TimetableEntry


class CreateAlterationSerializer(serializers.Serializer):
    timetable_entry_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    period = serializers.IntegerField(required=True)
    room = serializers.CharField(required=True)
    teacher = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class EmergencyRoomChangeSerializer(serializers.Serializer):
    timetable_entry_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    new_room = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="Emergency room change")


class CreateCancellationSerializer(serializers.Serializer):
    timetable_entry_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class CreateMaintenanceSerializer(serializers.Serializer):
    room = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="Maintenance")
    exception_type = serializers.CharField(required=False, default="MAINTENANCE")


class CreateReservationSerializer(serializers.Serializer):
    room = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    event_name = serializers.CharField(required=True)
    reservation_type = serializers.CharField(required=False, default="SPECIAL_LECTURE")


class TimetableOverrideSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.short_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)

    class Meta:
        model = TimetableOverride
        fields = ['id', 'timetable_entry', 'date', 'period', 'semester', 'section', 'subject_name', 'teacher_name', 'room_number', 'reason', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'user_identifier', 'action', 'target_model', 'target_id', 'old_values', 'new_values', 'reason', 'created_at']
