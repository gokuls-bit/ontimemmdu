import datetime
from typing import Optional, Dict, Any, List, Union
from django.db.models import Q
from core.services.timetable.clock import get_current_datetime
from core.services.timetable.period_engine import get_current_period
from timetable.models import (
    Room, TimeSlot, TimetableEntry, TimetableOverride, ClassCancellation,
    AcademicHoliday, RoomReservation, RoomException
)
from .exceptions import RoomNotFound
from .conflict_engine import check_room_schedule_conflict


def resolve_room(room_val: Union[Room, str, int]) -> Room:
    """Resolves room_val parameter to a valid Room model instance."""
    if isinstance(room_val, Room):
        return room_val

    r_str = str(room_val).strip()
    room_obj = Room.objects.filter(
        Q(room_number__iexact=r_str) | Q(room_number__iexact=f"Lab-{r_str}") | Q(room_number__iexact=f"C-{r_str}")
    ).first()

    if not room_obj:
        raise RoomNotFound(f"Room '{room_val}' was not found in the department database.")

    return room_obj


def get_room_status(room_val: Union[Room, str, int], now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Determines global real-time room occupancy status.
    
    Answers: "Who is in Room 357 right now?", "When does it finish?", and "Is it free?"
    """
    room_obj = resolve_room(room_val)
    dt = get_current_datetime(now)
    curr_date = dt.date()
    curr_time = dt.time()

    period_info = get_current_period(dt)
    period_status = period_info["status"]
    day_code = period_info["day"]
    period_num = period_info.get("period")

    res = {
        "room": room_obj.room_number,
        "building": room_obj.building,
        "floor": room_obj.floor,
        "room_type": room_obj.get_room_type_display(),
        "capacity": room_obj.capacity,
        "status": "FREE",
        "current_class": None,
        "minutes_remaining": 0,
        "next_available_time": None,
    }

    if not room_obj.is_active:
        res["status"] = "CLOSED"
        return res

    # 1. Check Room Exception (Maintenance / Repair / Temporary Closure)
    ex = RoomException.objects.filter(
        room=room_obj,
        date=curr_date
    ).filter(
        Q(start_time__isnull=True) | Q(start_time__lte=curr_time, end_time__gt=curr_time)
    ).first()

    if ex:
        res["status"] = ex.exception_type  # MAINTENANCE, REPAIR, TEMPORARY_CLOSURE
        res["notes"] = ex.reason
        return res

    # 2. Check Room Reservation (Exam / Seminar / Departmental Event)
    resv = RoomReservation.objects.filter(
        room=room_obj,
        date=curr_date,
        start_time__lte=curr_time,
        end_time__gt=curr_time
    ).first()

    if resv:
        dt_end = datetime.datetime.combine(curr_date, resv.end_time, tzinfo=dt.tzinfo)
        rem_mins = int((dt_end - dt).total_seconds() // 60)
        res.update({
            "status": "RESERVED",
            "event_name": resv.event_name,
            "reservation_type": resv.get_reservation_type_display(),
            "reserved_by": resv.reserved_by,
            "minutes_remaining": max(0, rem_mins),
            "next_available_time": resv.end_time.strftime("%H:%M"),
        })
        return res

    # 3. Check Period Status (Holiday / Weekend / Lunch / Break)
    if period_status == "HOLIDAY":
        res["status"] = "HOLIDAY"
        res["holiday_name"] = period_info.get("holiday_name")
        return res

    if period_status == "WEEKEND":
        res["status"] = "WEEKEND"
        return res

    if period_status in {"BEFORE_FIRST_PERIOD", "AFTER_LAST_PERIOD"}:
        res["status"] = "FREE"
        return res

    # 4. Evaluate Timetable Occupancy during ACTIVE_CLASS
    if period_num:
        # Check Override
        override = TimetableOverride.objects.filter(
            room=room_obj,
            date=curr_date,
            period=period_num
        ).select_related('subject', 'teacher', 'section', 'group', 'semester').first()

        if override:
            dt_end = datetime.datetime.combine(curr_date, period_info["end_time"], tzinfo=dt.tzinfo) if period_info.get("end_time") else None
            res.update({
                "status": "OCCUPIED",
                "current_class": {
                    "semester": f"{override.semester.number}th Semester",
                    "section": override.section.name if override.section else None,
                    "group": override.group.name if override.group else None,
                    "subject": override.subject.code,
                    "subject_name": override.subject.name,
                    "teacher": override.teacher.full_name,
                    "class_type": override.get_class_type_display(),
                    "participating_sections": [override.section.name] if override.section else [],
                    "start_time": period_info.get("start_time"),
                    "end_time": period_info.get("end_time"),
                },
                "minutes_remaining": period_info.get("remaining_minutes", 0),
                "next_available_time": period_info.get("end_time"),
            })
            return res

        # Query active TimetableEntries for this room
        entries = list(TimetableEntry.objects.filter(
            room=room_obj,
            day=day_code,
            period=period_num
        ).select_related('subject', 'teacher', 'section', 'group', 'merge_group', 'semester').prefetch_related('merge_group__groups'))

        active_entry = None
        for e in entries:
            if not ClassCancellation.objects.filter(timetable_entry=e, date=curr_date).exists():
                active_entry = e
                break

        if active_entry:
            # Collect participating sections for merged groups
            participating = []
            if active_entry.merge_group:
                groups = active_entry.merge_group.groups.select_related('section').all()
                participating = list({g.section.name for g in groups})
            elif active_entry.section:
                participating = [active_entry.section.name]

            res.update({
                "status": "OCCUPIED",
                "current_class": {
                    "semester": f"{active_entry.semester.number}th Semester",
                    "section": active_entry.section.name if active_entry.section else None,
                    "group": active_entry.group.name if active_entry.group else None,
                    "subject": active_entry.subject.code,
                    "subject_name": active_entry.subject.name,
                    "teacher": active_entry.teacher.full_name if active_entry.teacher else "Faculty Staff",
                    "class_type": active_entry.get_class_type_display(),
                    "participating_sections": participating,
                    "start_time": period_info.get("start_time"),
                    "end_time": period_info.get("end_time"),
                },
                "minutes_remaining": period_info.get("remaining_minutes", 0),
                "next_available_time": period_info.get("end_time"),
            })
            return res

    res["status"] = "FREE"
    return res


def search_rooms(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Searches rooms by room number, building, or room type using Django ORM.
    """
    if not query or not str(query).strip():
        return []

    q_str = str(query).strip()
    rooms = Room.objects.filter(
        Q(room_number__icontains=q_str) |
        Q(building__icontains=q_str) |
        Q(room_type__icontains=q_str)
    ).order_by('room_number')[:limit]

    return [
        {
            "room_number": r.room_number,
            "building": r.building,
            "floor": r.floor,
            "room_type": r.get_room_type_display(),
            "capacity": r.capacity,
            "is_active": r.is_active,
        }
        for r in rooms
    ]


def get_room_day_schedule(room_val: Union[Room, str, int], day_val: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns the complete day usage schedule of a room ordered by period.
    """
    room_obj = resolve_room(room_val)
    dt = get_current_datetime()
    curr_date = dt.date()
    day_code = day_val.upper()[:3] if day_val else get_current_period(dt)["day"]

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    entries = list(TimetableEntry.objects.filter(
        room=room_obj,
        day=day_code
    ).select_related('subject', 'teacher', 'section', 'group', 'merge_group', 'semester').prefetch_related('merge_group__groups'))

    overrides = list(TimetableOverride.objects.filter(
        room=room_obj,
        date=curr_date
    ).select_related('subject', 'teacher', 'section'))

    cancellations = set(ClassCancellation.objects.filter(
        date=curr_date,
        timetable_entry__room=room_obj
    ).values_list('timetable_entry_id', flat=True))

    schedule = []
    for slot in time_slots:
        p_num = slot.period
        override = next((o for o in overrides if o.period == p_num), None)
        entry = next((e for e in entries if e.period == p_num and e.id not in cancellations), None)

        status = "FREE"
        sub_code = None
        teacher_name = None
        sec_name = None
        participating = []

        if override:
            status = "OCCUPIED"
            sub_code = override.subject.code
            teacher_name = override.teacher.full_name
            sec_name = override.section.name if override.section else None
            participating = [sec_name] if sec_name else []
        elif entry:
            status = "OCCUPIED"
            sub_code = entry.subject.code
            teacher_name = entry.teacher.full_name if entry.teacher else None
            sec_name = entry.section.name if entry.section else None
            if entry.merge_group:
                groups = entry.merge_group.groups.select_related('section').all()
                participating = list({g.section.name for g in groups})
            elif sec_name:
                participating = [sec_name]

        schedule.append({
            "period": p_num,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "status": status,
            "subject": sub_code,
            "teacher": teacher_name,
            "section": sec_name,
            "participating_sections": participating,
        })

    return schedule


def get_room_next_free(room_val: Union[Room, str, int], now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Searches forward through the timetable until a genuinely free interval is found.
    If occupied continuously P2->P3->P4, returns next_free_time = end of P4.
    """
    room_obj = resolve_room(room_val)
    dt = get_current_datetime(now)
    curr_status = get_room_status(room_obj, dt)

    if curr_status["status"] == "FREE":
        return {
            "room": room_obj.room_number,
            "status": "FREE",
            "next_free_time": dt.time().strftime("%H:%M"),
            "currently_occupied": False
        }

    # If occupied, search forward period by period until room becomes free
    period_info = get_current_period(dt)
    day_code = period_info["day"]
    curr_period = period_info.get("period") or 1

    time_slots = list(TimeSlot.objects.filter(day=day_code, period__gte=curr_period).order_by('period'))
    next_free_time = period_info.get("end_time") or "17:40"

    for slot in time_slots:
        # Check if slot is occupied
        entry = TimetableEntry.objects.filter(room=room_obj, day=day_code, period=slot.period).first()
        override = TimetableOverride.objects.filter(room=room_obj, date=dt.date(), period=slot.period).first()

        if override or entry:
            next_free_time = slot.end_time.strftime("%H:%M")
        else:
            # Found first genuinely free slot
            next_free_time = slot.start_time.strftime("%H:%M")
            break

    return {
        "room": room_obj.room_number,
        "status": curr_status["status"],
        "next_free_time": next_free_time,
        "currently_occupied": True
    }


def get_room_next_class(room_val: Union[Room, str, int], now: Optional[datetime.datetime] = None) -> Optional[Dict[str, Any]]:
    """
    Returns the upcoming class scheduled in this room.
    """
    room_obj = resolve_room(room_val)
    dt = get_current_datetime(now)
    period_info = get_current_period(dt)
    day_code = period_info["day"]
    curr_period = period_info.get("period") or 0

    future_slots = TimeSlot.objects.filter(day=day_code, period__gt=curr_period).order_by('period')

    for slot in future_slots:
        override = TimetableOverride.objects.filter(room=room_obj, date=dt.date(), period=slot.period).select_related('subject', 'teacher', 'section').first()
        if override:
            return {
                "period": slot.period,
                "subject": override.subject.code,
                "teacher": override.teacher.full_name,
                "section": override.section.name if override.section else None,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
            }

        entry = TimetableEntry.objects.filter(room=room_obj, day=day_code, period=slot.period).select_related('subject', 'teacher', 'section').first()
        if entry:
            return {
                "period": slot.period,
                "subject": entry.subject.code,
                "teacher": entry.teacher.full_name if entry.teacher else None,
                "section": entry.section.name if entry.section else None,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
            }

    return None


def get_room_utilization(room_val: Union[Room, str, int], date_val: Optional[datetime.date] = None) -> Dict[str, Any]:
    """
    Calculates occupied vs available minutes and utilization percentage for a room.
    """
    room_obj = resolve_room(room_val)
    d = date_val or get_current_datetime().date()
    day_code = get_current_period(datetime.datetime.combine(d, datetime.time(10, 0)))["day"]

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    total_mins = len(time_slots) * 60
    occupied_mins = 0

    entries = list(TimetableEntry.objects.filter(room=room_obj, day=day_code))
    overrides = list(TimetableOverride.objects.filter(room=room_obj, date=d))

    for slot in time_slots:
        has_occ = any(o.period == slot.period for o in overrides) or any(e.period == slot.period for e in entries)
        if has_occ:
            occupied_mins += 60

    free_mins = max(0, total_mins - occupied_mins)
    pct = round((occupied_mins / total_mins * 100), 2) if total_mins > 0 else 0.0

    return {
        "room": room_obj.room_number,
        "date": d.isoformat(),
        "total_available_minutes": total_mins,
        "occupied_minutes": occupied_mins,
        "free_minutes": free_mins,
        "utilization_percentage": pct,
    }
