from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.api.throttles import StudentAnonRateThrottle
from core.api.serializers import (
    RoomSearchQuerySerializer, FreeRoomsQuerySerializer, FindAvailableRoomsQuerySerializer
)
from core.services.location import (
    get_room_status, search_rooms, get_room_day_schedule,
    get_room_next_free, get_room_next_class, get_room_utilization,
    get_all_room_statuses, get_occupied_rooms, get_free_rooms,
    get_room_availability, find_available_rooms
)


class RoomStatusAPIView(APIView):
    """GET /api/v1/rooms/<room>/status/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, room):
        data = get_room_status(room_val=room)
        return Response(data)


class FreeRoomsAPIView(APIView):
    """GET /api/v1/rooms/free/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = FreeRoomsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        room_type = serializer.validated_data.get('room_type')
        data = get_free_rooms(room_type=room_type)
        return Response(data)


class OccupiedRoomsAPIView(APIView):
    """GET /api/v1/rooms/occupied/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        room_type = request.query_params.get('room_type')
        data = get_occupied_rooms(room_type=room_type)
        return Response(data)


class AllRoomStatusAPIView(APIView):
    """GET /api/v1/rooms/status/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        status_filter = request.query_params.get('status')
        room_type_filter = request.query_params.get('room_type')
        data = get_all_room_statuses(status=status_filter, room_type=room_type_filter)
        return Response(data)


class RoomScheduleAPIView(APIView):
    """GET /api/v1/rooms/<room>/schedule/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, room):
        day = request.query_params.get('day')
        data = get_room_day_schedule(room_val=room, day_val=day)
        return Response({
            "room": room,
            "day": day or "Today",
            "schedule": data
        })


class RoomNextFreeAPIView(APIView):
    """GET /api/v1/rooms/<room>/next-free/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, room):
        data = get_room_next_free(room_val=room)
        return Response(data)


class RoomNextClassAPIView(APIView):
    """GET /api/v1/rooms/<room>/next-class/"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request, room):
        data = get_room_next_class(room_val=room)
        return Response(data if data is not None else {})


class RoomSearchAPIView(APIView):
    """GET /api/v1/rooms/search/?q=357"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = RoomSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        q = serializer.validated_data['q']
        data = search_rooms(query=q)
        return Response(data)


class RoomAvailabilityAPIView(APIView):
    """GET /api/v1/rooms/availability/?room=357"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        room = request.query_params.get('room') or request.query_params.get('q')
        if not room:
            return Response({"error": "Room identifier parameter 'room' is required."}, status=400)

        data = get_room_availability(room_val=room)
        return Response(data)


class FindAvailableRoomsAPIView(APIView):
    """GET /api/v1/rooms/find-available/?start_time=11:00&end_time=13:00&room_type=LABORATORY"""
    permission_classes = [AllowAny]
    throttle_classes = [StudentAnonRateThrottle]

    def get(self, request):
        serializer = FindAvailableRoomsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        st = serializer.validated_data['start_time']
        et = serializer.validated_data['end_time']
        room_type = serializer.validated_data.get('room_type')
        date_val = serializer.validated_data.get('date')

        data = find_available_rooms(start_time=st, end_time=et, room_type=room_type, date_val=date_val)
        return Response(data)
