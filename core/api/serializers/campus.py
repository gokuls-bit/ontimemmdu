from rest_framework import serializers
from .room import RoomStatusSerializer
from .teacher import TeacherLocationSerializer


class CampusOccupancySerializer(serializers.Serializer):
    server_time = serializers.CharField()
    timezone = serializers.CharField()
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    free_rooms = serializers.IntegerField()
    unavailable_rooms = serializers.IntegerField()
    active_classes = serializers.IntegerField()
    active_teachers = serializers.IntegerField()
    utilization_percentage = serializers.FloatField()


class LocationIntelligenceStateSerializer(serializers.Serializer):
    server_time = serializers.CharField()
    timezone = serializers.CharField()
    room_status = RoomStatusSerializer(allow_null=True, required=False)
    teacher_status = TeacherLocationSerializer(allow_null=True, required=False)
    campus_occupancy = CampusOccupancySerializer()
