import datetime
from typing import Optional, Dict, Any, List, Union
from core.services.timetable.clock import get_current_datetime
from core.services.timetable.period_engine import get_current_period
from timetable.models import Room, Teacher
from .room_engine import get_room_status
from .teacher_engine import get_teacher_current_location, get_all_teacher_statuses


def get_all_room_statuses(
    now: Optional[datetime.datetime] = None,
    status: Optional[str] = None,
    room_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Returns real-time status listing for ALL registered department rooms.
    
    Supports filtering by status (OCCUPIED, FREE, RESERVED, MAINTENANCE, CLOSED) and room_type.
    """
    dt = get_current_datetime(now)
    query = Room.objects.all().order_by('room_number')

    if room_type:
        query = query.filter(room_type__iexact=room_type)

    rooms = list(query)
    statuses = [get_room_status(r, dt) for r in rooms]

    if status:
        st_upper = status.upper().strip()
        statuses = [s for s in statuses if s["status"].upper() == st_upper]

    return statuses


def get_occupied_rooms(now: Optional[datetime.datetime] = None, room_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns list of all currently occupied rooms sorted naturally by room number.
    """
    return get_all_room_statuses(now=now, status="OCCUPIED", room_type=room_type)


def get_campus_occupancy_state(now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Returns global administrative campus occupancy state.
    
    Powers executive/admin dashboard visualizations.
    """
    dt = get_current_datetime(now)
    all_rooms = get_all_room_statuses(dt)

    total_rooms = len(all_rooms)
    occupied_rooms = len([r for r in all_rooms if r["status"] == "OCCUPIED"])
    free_rooms = len([r for r in all_rooms if r["status"] == "FREE"])
    unavailable_rooms = len([r for r in all_rooms if r["status"] in {"CLOSED", "MAINTENANCE", "REPAIR", "TEMPORARY_CLOSURE"}])

    all_teachers = get_all_teacher_statuses(dt)
    active_teachers = len([t for t in all_teachers if t["status"] == "TEACHING"])

    utilization_pct = round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0.0

    return {
        "server_time": dt.isoformat(),
        "timezone": "Asia/Kolkata",
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "free_rooms": free_rooms,
        "unavailable_rooms": unavailable_rooms,
        "active_classes": occupied_rooms,
        "active_teachers": active_teachers,
        "utilization_percentage": utilization_pct,
    }


def get_location_intelligence_state(
    room_val: Optional[Union[Room, str, int]] = None,
    teacher_val: Optional[Union[Teacher, str, int]] = None,
    now: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    """
    Combined convenience service returning normalized room, teacher, and campus state.
    """
    dt = get_current_datetime(now)

    room_data = get_room_status(room_val, dt) if room_val else None
    teacher_data = get_teacher_current_location(teacher_val, dt) if teacher_val else None
    campus_data = get_campus_occupancy_state(dt)

    return {
        "server_time": dt.isoformat(),
        "timezone": "Asia/Kolkata",
        "room_status": room_data,
        "teacher_status": teacher_data,
        "campus_occupancy": campus_data,
    }
