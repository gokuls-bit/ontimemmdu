from rest_framework import serializers


class RoomSearchQuerySerializer(serializers.Serializer):
    """Validates room search query string."""
    q = serializers.CharField(required=True, help_text="Search string for room number, building, or type")


class FreeRoomsQuerySerializer(serializers.Serializer):
    """Validates free rooms query parameters."""
    room_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)


class FindAvailableRoomsQuerySerializer(serializers.Serializer):
    """Validates interval available rooms query parameters."""
    start_time = serializers.CharField(required=True, help_text="Start time in HH:MM format, e.g. 11:00")
    end_time = serializers.CharField(required=True, help_text="End time in HH:MM format, e.g. 13:00")
    room_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)


class RoomStatusSerializer(serializers.Serializer):
    room = serializers.CharField()
    building = serializers.CharField()
    floor = serializers.IntegerField()
    room_type = serializers.CharField()
    capacity = serializers.IntegerField()
    status = serializers.CharField()
    current_class = serializers.DictField(allow_null=True, required=False)
    minutes_remaining = serializers.IntegerField(required=False)
    next_available_time = serializers.CharField(allow_null=True, required=False)


class RoomScheduleEntrySerializer(serializers.Serializer):
    period = serializers.IntegerField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    status = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    teacher = serializers.CharField(allow_null=True)
    section = serializers.CharField(allow_null=True)
    participating_sections = serializers.ListField(child=serializers.CharField(), required=False)


class RoomNextFreeSerializer(serializers.Serializer):
    room = serializers.CharField()
    status = serializers.CharField()
    next_free_time = serializers.CharField()
    currently_occupied = serializers.BooleanField()
