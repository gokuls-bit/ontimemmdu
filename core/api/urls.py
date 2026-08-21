from django.urls import path
from .views import (
    StudentCurrentClassAPIView, StudentNextClassAPIView, StudentStateAPIView, StudentScheduleAPIView,
    RoomStatusAPIView, FreeRoomsAPIView, OccupiedRoomsAPIView, AllRoomStatusAPIView,
    RoomScheduleAPIView, RoomNextFreeAPIView, RoomNextClassAPIView, RoomSearchAPIView,
    RoomAvailabilityAPIView, FindAvailableRoomsAPIView,
    TeacherSearchAPIView, TeacherLocationAPIView, TeacherNextClassAPIView, TeacherScheduleAPIView, AllTeacherStatusAPIView,
    CampusOccupancyAPIView, LocationIntelligenceStateAPIView,
    MetadataSemestersAPIView, MetadataSectionsAPIView, MetadataGroupsAPIView,
    TimetableDownloadAPIView, HealthCheckAPIView
)

urlpatterns = [
    # Health Check
    path('v1/health/', HealthCheckAPIView.as_view(), name='api-health'),

    # Student Endpoints
    path('v1/student/current-class/', StudentCurrentClassAPIView.as_view(), name='api-student-current-class'),
    path('v1/student/next-class/', StudentNextClassAPIView.as_view(), name='api-student-next-class'),
    path('v1/student/state/', StudentStateAPIView.as_view(), name='api-student-state'),
    path('v1/student/schedule/', StudentScheduleAPIView.as_view(), name='api-student-schedule'),

    # Room Endpoints
    path('v1/rooms/search/', RoomSearchAPIView.as_view(), name='api-room-search'),
    path('v1/rooms/free/', FreeRoomsAPIView.as_view(), name='api-room-free'),
    path('v1/rooms/occupied/', OccupiedRoomsAPIView.as_view(), name='api-room-occupied'),
    path('v1/rooms/status/', AllRoomStatusAPIView.as_view(), name='api-room-status-list'),
    path('v1/rooms/availability/', RoomAvailabilityAPIView.as_view(), name='api-room-availability'),
    path('v1/rooms/find-available/', FindAvailableRoomsAPIView.as_view(), name='api-room-find-available'),
    path('v1/rooms/<str:room>/status/', RoomStatusAPIView.as_view(), name='api-room-status'),
    path('v1/rooms/<str:room>/schedule/', RoomScheduleAPIView.as_view(), name='api-room-schedule'),
    path('v1/rooms/<str:room>/next-free/', RoomNextFreeAPIView.as_view(), name='api-room-next-free'),
    path('v1/rooms/<str:room>/next-class/', RoomNextClassAPIView.as_view(), name='api-room-next-class'),

    # Teacher Endpoints
    path('v1/teachers/search/', TeacherSearchAPIView.as_view(), name='api-teacher-search'),
    path('v1/teachers/status/', AllTeacherStatusAPIView.as_view(), name='api-teacher-status-list'),
    path('v1/teachers/<str:teacher>/location/', TeacherLocationAPIView.as_view(), name='api-teacher-location'),
    path('v1/teachers/<str:teacher>/next-class/', TeacherNextClassAPIView.as_view(), name='api-teacher-next-class'),
    path('v1/teachers/<str:teacher>/schedule/', TeacherScheduleAPIView.as_view(), name='api-teacher-schedule'),

    # Campus Endpoints
    path('v1/campus/occupancy/', CampusOccupancyAPIView.as_view(), name='api-campus-occupancy'),
    path('v1/campus/intelligence/', LocationIntelligenceStateAPIView.as_view(), name='api-campus-intelligence'),

    # Metadata Endpoints
    path('v1/metadata/semesters/', MetadataSemestersAPIView.as_view(), name='api-metadata-semesters'),
    path('v1/metadata/sections/', MetadataSectionsAPIView.as_view(), name='api-metadata-sections'),
    path('v1/metadata/groups/', MetadataGroupsAPIView.as_view(), name='api-metadata-groups'),

    # Timetable Downloads
    path('v1/timetable/<str:semester>/<str:fmt>/', TimetableDownloadAPIView.as_view(), name='api-timetable-download'),
]
