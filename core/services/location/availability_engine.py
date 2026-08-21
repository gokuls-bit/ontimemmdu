import datetime
from typing import Optional, Dict, Any, List, Union
from django.db.models import Q
from core.services.timetable.clock import get_current_datetime
from core.services.timetable.period_engine import get_current_period
from timetable.models import (
    Room, TimeSlot, TimetableEntry, TimetableOverride, ClassCancellation,
    RoomReservation, RoomException
)
from .room_engine import resolve_room, get_room_status


def get_free_rooms(now: Optional[datetime.datetime] = None, room_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns rooms that are genuinely free right now.
    
    A room is FREE only if:
    - no active timetable class
    - AND no active room reservation
    - AND no active maintenance/repair exception
    - AND room is active
    """
    dt = get_current_datetime(now)
    query = Room.objects.filter(is_active=True)

    if room_type:
        query = query.filter(room_type__iexact=room_type)

    rooms = list(query.order_by('room_number'))
    free_rooms = []

    for r in rooms:
        status_info = get_room_status(r, dt)
        if status_info["status"] == "FREE":
            free_rooms.append({
                "room": r.room_number,
                "building": r.building,
                "floor": r.floor,
                "room_type": r.get_room_type_display(),
                "capacity": r.capacity,
                "status": "FREE",
                "next_scheduled_use": status_info.get("next_available_time"),
            })

    return free_rooms


def get_room_availability(room_val: Union[Room, str, int], date_val: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
    """
    Returns continuous free and occupied time windows for a room across the day.
    """
    room_obj = resolve_room(room_val)
    d = date_val or get_current_datetime().date()
    day_code = get_current_period(datetime.datetime.combine(d, datetime.time(10, 0)))["day"]

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    entries = list(TimetableEntry.objects.filter(room=room_obj, day=day_code))
    overrides = list(TimetableOverride.objects.filter(room=room_obj, date=d))
    reservations = list(RoomReservation.objects.filter(room=room_obj, date=d))
    exceptions = list(RoomException.objects.filter(room=room_obj, date=d))

    windows = []
    for slot in time_slots:
        st = slot.start_time
        et = slot.end_time

        # Check Exception
        is_ex = any(
            (e.start_time is None and e.end_time is None) or
            (e.start_time and e.start_time <= st and e.end_time >= et)
            for e in exceptions
        )

        # Check Reservation
        is_resv = any(r.start_time <= st and r.end_time >= et for r in reservations)

        # Check Timetable Class / Override
        is_class = any(o.period == slot.period for o in overrides) or any(e.period == slot.period for e in entries)

        slot_status = "FREE"
        if is_ex:
            slot_status = "MAINTENANCE"
        elif is_resv:
            slot_status = "RESERVED"
        elif is_class:
            slot_status = "OCCUPIED"

        windows.append({
            "period": slot.period,
            "start_time": st.strftime("%H:%M"),
            "end_time": et.strftime("%H:%M"),
            "status": slot_status,
        })

    return windows


def find_available_rooms(
    start_time: Union[datetime.time, str],
    end_time: Union[datetime.time, str],
    room_type: Optional[str] = None,
    date_val: Optional[datetime.date] = None
) -> List[Dict[str, Any]]:
    """
    Finds rooms that are genuinely free for the COMPLETE requested time interval.
    
    If requested 11:00 - 13:00, and a room is occupied from 12:00 - 13:00, it is NOT returned.
    """
    d = date_val or get_current_datetime().date()

    if isinstance(start_time, str):
        h, m = map(int, start_time.split(':')[:2])
        st_obj = datetime.time(h, m)
    else:
        st_obj = start_time

    if isinstance(end_time, str):
        h, m = map(int, end_time.split(':')[:2])
        et_obj = datetime.time(h, m)
    else:
        et_obj = end_time

    query = Room.objects.filter(is_active=True)
    if room_type:
        query = query.filter(room_type__iexact=room_type)

    rooms = list(query.order_by('room_number'))
    day_code = get_current_period(datetime.datetime.combine(d, st_obj))["day"]

    available_rooms = []

    for r in rooms:
        # Check Room Exception
        has_exception = RoomException.objects.filter(
            room=r,
            date=d
        ).filter(
            Q(start_time__isnull=True) |
            Q(start_time__lt=et_obj, end_time__gt=st_obj)
        ).exists()

        if has_exception:
            continue

        # Check Room Reservation
        has_reservation = RoomReservation.objects.filter(
            room=r,
            date=d,
            start_time__lt=et_obj,
            end_time__gt=st_obj
        ).exists()

        if has_reservation:
            continue

        # Check Timetable Entries overlapping requested time interval
        overlapping_slots = TimeSlot.objects.filter(
            day=day_code,
            start_time__lt=et_obj,
            end_time__gt=st_obj
        )

        slot_periods = [s.period for s in overlapping_slots]

        has_override = TimetableOverride.objects.filter(
            room=r,
            date=d,
            period__in=slot_periods
        ).exists()

        if has_override:
            continue

        has_entry = TimetableEntry.objects.filter(
            room=r,
            day=day_code,
            period__in=slot_periods
        ).exists()

        if has_entry:
            continue

        # Room is free for the ENTIRE requested interval
        available_rooms.append({
            "room": r.room_number,
            "building": r.building,
            "floor": r.floor,
            "room_type": r.get_room_type_display(),
            "capacity": r.capacity,
            "status": "AVAILABLE",
            "requested_interval": f"{st_obj.strftime('%H:%M')} - {et_obj.strftime('%H:%M')}",
        })

    return available_rooms
