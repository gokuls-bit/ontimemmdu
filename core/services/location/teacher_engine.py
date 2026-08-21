import datetime
from typing import Optional, Dict, Any, List, Union
from django.db.models import Q
from core.services.timetable.clock import get_current_datetime
from core.services.timetable.period_engine import get_current_period
from timetable.models import (
    Teacher, TimeSlot, TimetableEntry, TimetableOverride, ClassCancellation, AcademicHoliday
)
from .exceptions import TeacherNotFound


def resolve_teacher(teacher_val: Union[Teacher, str, int]) -> Teacher:
    """Resolves teacher_val parameter to a valid Teacher model instance."""
    if isinstance(teacher_val, Teacher):
        return teacher_val

    t_str = str(teacher_val).strip()
    # Try employee ID match first
    teacher = Teacher.objects.filter(employee_id__iexact=t_str).first()
    if not teacher:
        # Try full name or first/last name match
        parts = t_str.replace("Dr.", "").replace("Dr", "").replace("Mr.", "").replace("Ms.", "").strip().split()
        if len(parts) == 1:
            teacher = Teacher.objects.filter(
                Q(first_name__icontains=parts[0]) | Q(last_name__icontains=parts[0])
            ).first()
        elif len(parts) >= 2:
            teacher = Teacher.objects.filter(
                Q(first_name__icontains=parts[0], last_name__icontains=parts[1]) |
                Q(first_name__icontains=parts[1], last_name__icontains=parts[0])
            ).first()

    if not teacher:
        raise TeacherNotFound(f"Teacher '{teacher_val}' was not found in the department faculty directory.")

    return teacher


def get_teacher_current_location(teacher_val: Union[Teacher, str, int], now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Determines real-time location and current teaching activity of a faculty member.
    
    Answers: "Where is Dr. Sharma right now?", "What room is he in?", and "Where is his next class?"
    """
    teacher_obj = resolve_teacher(teacher_val)
    dt = get_current_datetime(now)
    curr_date = dt.date()

    period_info = get_current_period(dt)
    period_status = period_info["status"]
    day_code = period_info["day"]
    period_num = period_info.get("period")

    res = {
        "teacher": teacher_obj.full_name,
        "employee_id": teacher_obj.employee_id,
        "designation": teacher_obj.designation,
        "department": teacher_obj.department,
        "status": "FREE",
        "room": None,
        "semester": None,
        "section": None,
        "group": None,
        "subject": None,
        "subject_name": None,
        "start_time": None,
        "end_time": None,
        "minutes_remaining": 0,
        "next_class": None,
    }

    if not teacher_obj.is_active:
        res["status"] = "ON_LEAVE"
        return res

    if period_status == "HOLIDAY":
        res["status"] = "HOLIDAY"
        res["holiday_name"] = period_info.get("holiday_name")
        return res

    if period_status == "WEEKEND":
        res["status"] = "WEEKEND"
        return res

    # Evaluate teaching status during ACTIVE_CLASS
    if period_num:
        # Check Override
        override = TimetableOverride.objects.filter(
            teacher=teacher_obj,
            date=curr_date,
            period=period_num
        ).select_related('room', 'subject', 'section', 'group', 'semester').first()

        if override:
            res.update({
                "status": "TEACHING",
                "room": override.room.room_number,
                "semester": f"{override.semester.number}th Semester",
                "section": override.section.name if override.section else None,
                "group": override.group.name if override.group else None,
                "subject": override.subject.code,
                "subject_name": override.subject.name,
                "start_time": period_info.get("start_time"),
                "end_time": period_info.get("end_time"),
                "minutes_remaining": period_info.get("remaining_minutes", 0),
            })
            return res

        # Query active TimetableEntry for teacher
        entry = TimetableEntry.objects.filter(
            teacher=teacher_obj,
            day=day_code,
            period=period_num
        ).select_related('room', 'subject', 'section', 'group', 'merge_group', 'semester').first()

        if entry and not ClassCancellation.objects.filter(timetable_entry=entry, date=curr_date).exists():
            res.update({
                "status": "TEACHING",
                "room": entry.room.room_number if entry.room else None,
                "semester": f"{entry.semester.number}th Semester",
                "section": entry.section.name if entry.section else None,
                "group": entry.group.name if entry.group else None,
                "subject": entry.subject.code,
                "subject_name": entry.subject.name,
                "start_time": period_info.get("start_time"),
                "end_time": period_info.get("end_time"),
                "minutes_remaining": period_info.get("remaining_minutes", 0),
            })
            return res

    # Resolve Next Class Location
    nxt = get_teacher_next_class(teacher_obj, dt)
    res["next_class"] = nxt
    res["status"] = "FREE"
    return res


def search_teachers(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Searches teachers by name or employee ID using Django ORM.
    """
    if not query or not str(query).strip():
        return []

    q_str = str(query).strip()
    teachers = Teacher.objects.filter(
        Q(first_name__icontains=q_str) |
        Q(last_name__icontains=q_str) |
        Q(employee_id__icontains=q_str) |
        Q(email__icontains=q_str)
    ).order_by('first_name')[:limit]

    return [
        {
            "employee_id": t.employee_id,
            "full_name": t.full_name,
            "designation": t.designation,
            "department": t.department,
            "email": t.email,
        }
        for t in teachers
    ]


def get_teacher_day_schedule(teacher_val: Union[Teacher, str, int], day_val: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns complete period schedule for a teacher ordered by period.
    """
    teacher_obj = resolve_teacher(teacher_val)
    dt = get_current_datetime()
    curr_date = dt.date()
    day_code = day_val.upper()[:3] if day_val else get_current_period(dt)["day"]

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    entries = list(TimetableEntry.objects.filter(
        teacher=teacher_obj,
        day=day_code
    ).select_related('subject', 'room', 'section', 'group', 'semester'))

    overrides = list(TimetableOverride.objects.filter(
        teacher=teacher_obj,
        date=curr_date
    ).select_related('subject', 'room', 'section'))

    cancellations = set(ClassCancellation.objects.filter(
        date=curr_date,
        timetable_entry__teacher=teacher_obj
    ).values_list('timetable_entry_id', flat=True))

    schedule = []
    for slot in time_slots:
        p_num = slot.period
        override = next((o for o in overrides if o.period == p_num), None)
        entry = next((e for e in entries if e.period == p_num and e.id not in cancellations), None)

        status = "FREE"
        sub_code = None
        room_no = None
        sec_name = None

        if override:
            status = "TEACHING"
            sub_code = override.subject.code
            room_no = override.room.room_number
            sec_name = override.section.name if override.section else None
        elif entry:
            status = "TEACHING"
            sub_code = entry.subject.code
            room_no = entry.room.room_number if entry.room else None
            sec_name = entry.section.name if entry.section else None

        schedule.append({
            "period": p_num,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "status": status,
            "subject": sub_code,
            "room": room_no,
            "section": sec_name,
        })

    return schedule


def get_teacher_next_class(teacher_val: Union[Teacher, str, int], now: Optional[datetime.datetime] = None) -> Optional[Dict[str, Any]]:
    """
    Returns upcoming class location and details for a teacher today.
    """
    teacher_obj = resolve_teacher(teacher_val)
    dt = get_current_datetime(now)
    period_info = get_current_period(dt)
    day_code = period_info["day"]
    curr_period = period_info.get("period") or 0

    future_slots = TimeSlot.objects.filter(day=day_code, period__gt=curr_period).order_by('period')

    for slot in future_slots:
        override = TimetableOverride.objects.filter(teacher=teacher_obj, date=dt.date(), period=slot.period).select_related('subject', 'room', 'section').first()
        if override:
            dt_start = datetime.datetime.combine(dt.date(), slot.start_time, tzinfo=dt.tzinfo)
            mins_until = int((dt_start - dt).total_seconds() // 60)
            return {
                "period": slot.period,
                "subject": override.subject.code,
                "room": override.room.room_number,
                "section": override.section.name if override.section else None,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "minutes_until_start": max(0, mins_until),
            }

        entry = TimetableEntry.objects.filter(teacher=teacher_obj, day=day_code, period=slot.period).select_related('subject', 'room', 'section').first()
        if entry and not ClassCancellation.objects.filter(timetable_entry=entry, date=dt.date()).exists():
            dt_start = datetime.datetime.combine(dt.date(), slot.start_time, tzinfo=dt.tzinfo)
            mins_until = int((dt_start - dt).total_seconds() // 60)
            return {
                "period": slot.period,
                "subject": entry.subject.code,
                "room": entry.room.room_number if entry.room else None,
                "section": entry.section.name if entry.section else None,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "minutes_until_start": max(0, mins_until),
            }

    return None


def get_all_teacher_statuses(now: Optional[datetime.datetime] = None) -> List[Dict[str, Any]]:
    """
    Returns global campus-wide location statuses for all active department faculty.
    """
    dt = get_current_datetime(now)
    teachers = Teacher.objects.filter(is_active=True).order_by('first_name', 'last_name')
    return [get_teacher_current_location(t, dt) for t in teachers]
