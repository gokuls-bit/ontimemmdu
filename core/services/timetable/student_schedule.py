import datetime
from typing import Optional, Dict, Any, List
from django.db.models import Q
from .clock import get_current_datetime
from .period_engine import get_current_period
from .group_resolver import validate_student_context, resolve_group_entry
from timetable.models import TimeSlot, TimetableEntry, TimetableOverride, ClassCancellation, AcademicHoliday


def get_current_class(
    semester_val: Any,
    section_val: Any,
    group_val: Optional[Any] = None,
    now: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    """
    Determines what a student should be attending right NOW.
    
    Answers: Where should I be right now, when should I leave, and who is teaching?
    """
    sem_obj, sec_obj, grp_obj = validate_student_context(semester_val, section_val, group_val)
    dt = get_current_datetime(now)
    period_info = get_current_period(dt)

    status = period_info["status"]
    day_code = period_info["day"]
    period_num = period_info["period"]
    curr_date = dt.date()

    res = {
        "status": status,
        "semester": f"{sem_obj.number}th Semester",
        "section": sec_obj.name,
        "group": grp_obj.name if grp_obj else None,
        "period": period_num,
        "subject": None,
        "subject_name": None,
        "teacher": None,
        "room": None,
        "class_type": None,
        "start_time": period_info.get("start_time"),
        "end_time": period_info.get("end_time"),
        "minutes_elapsed": period_info.get("elapsed_minutes", 0),
        "minutes_remaining": period_info.get("remaining_minutes", 0),
        "holiday_name": period_info.get("holiday_name"),
    }

    if status in {"HOLIDAY", "WEEKEND", "BEFORE_FIRST_PERIOD", "AFTER_LAST_PERIOD", "NO_CONFIGURED_PERIODS"}:
        return res

    if status == "ACTIVE_CLASS" and period_num:
        entry, override, is_cancelled = resolve_group_entry(
            semester=sem_obj,
            section=sec_obj,
            group=grp_obj,
            day=day_code,
            period=period_num,
            date_val=curr_date
        )

        if is_cancelled:
            res["status"] = "CANCELLED"
            if entry:
                res["subject"] = entry.subject.code
                res["subject_name"] = entry.subject.name
                res["teacher"] = entry.teacher.full_name if entry.teacher else None
                res["room"] = entry.room.room_number if entry.room else None
            return res

        if override:
            res.update({
                "status": "ACTIVE_CLASS",
                "subject": override.subject.code,
                "subject_name": override.subject.name,
                "teacher": override.teacher.full_name,
                "room": override.room.room_number,
                "class_type": override.get_class_type_display(),
            })
            return res

        if entry:
            res.update({
                "status": "ACTIVE_CLASS",
                "subject": entry.subject.code,
                "subject_name": entry.subject.name,
                "teacher": entry.teacher.full_name if entry.teacher else None,
                "room": entry.room.room_number if entry.room else None,
                "class_type": entry.get_class_type_display(),
            })
        else:
            res["status"] = "FREE"

    return res


def get_next_class(
    semester_val: Any,
    section_val: Any,
    group_val: Optional[Any] = None,
    now: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    """
    Determines what class the student must attend NEXT today.
    
    Searches forward from the current point in time. Calculates minutes_until_start
    and detects intervening breaks/lunch.
    """
    sem_obj, sec_obj, grp_obj = validate_student_context(semester_val, section_val, group_val)
    dt = get_current_datetime(now)
    period_info = get_current_period(dt)

    status = period_info["status"]
    day_code = period_info["day"]
    curr_date = dt.date()
    curr_period = period_info.get("period") or 0

    res = {
        "status": "NO_MORE_CLASSES_TODAY",
        "period": None,
        "subject": None,
        "subject_name": None,
        "teacher": None,
        "room": None,
        "class_type": None,
        "start_time": None,
        "end_time": None,
        "minutes_until_start": 0,
        "intervening_break": None,
    }

    if status in {"HOLIDAY", "WEEKEND", "AFTER_LAST_PERIOD"}:
        return res

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    future_slots = [ts for ts in time_slots if ts.period > curr_period]

    if not future_slots and status == "BEFORE_FIRST_PERIOD":
        future_slots = time_slots

    intervening_break = None

    for slot in future_slots:
        entry, override, is_cancelled = resolve_group_entry(
            semester=sem_obj,
            section=sec_obj,
            group=grp_obj,
            day=day_code,
            period=slot.period,
            date_val=curr_date
        )

        if is_cancelled:
            continue

        if override or entry:
            sub = override.subject if override else entry.subject
            teach = override.teacher if override else entry.teacher
            rm = override.room if override else entry.room
            ctype = override.get_class_type_display() if override else entry.get_class_type_display()

            dt_start = datetime.datetime.combine(curr_date, slot.start_time, tzinfo=dt.tzinfo)
            mins_until = int((dt_start - dt).total_seconds() // 60)

            res.update({
                "status": "UPCOMING_CLASS",
                "period": slot.period,
                "subject": sub.code,
                "subject_name": sub.name,
                "teacher": teach.full_name if teach else None,
                "room": rm.room_number if rm else None,
                "class_type": ctype,
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "minutes_until_start": max(0, mins_until),
                "intervening_break": intervening_break,
            })
            return res
        else:
            if slot.period == 5:
                intervening_break = {
                    "type": "LUNCH",
                    "period": slot.period,
                    "start_time": slot.start_time.strftime("%H:%M"),
                    "end_time": slot.end_time.strftime("%H:%M"),
                }

    return res


def get_day_schedule(
    semester_val: Any,
    section_val: Any,
    group_val: Optional[Any] = None,
    day_val: Optional[str] = None,
    now: Optional[datetime.datetime] = None,
    order: str = "asc"
) -> List[Dict[str, Any]]:
    """
    Returns the complete day's schedule ordered by period.
    
    Fully optimized with pre-fetched querysets to eliminate N+1 database query overhead.
    """
    sem_obj, sec_obj, grp_obj = validate_student_context(semester_val, section_val, group_val)
    dt = get_current_datetime(now)
    curr_date = dt.date()

    if day_val:
        day_code = day_val.upper()[:3]
    else:
        period_info = get_current_period(dt)
        day_code = period_info["day"]

    # 1. Check Holiday in single query
    if AcademicHoliday.objects.filter(date=curr_date, is_active=True).exists():
        return [{
            "status": "HOLIDAY",
            "period": 0,
            "subject": None,
            "room": None,
            "notes": "Academic Holiday"
        }]

    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))
    curr_period_info = get_current_period(dt)
    active_p_num = curr_period_info.get("period") if curr_period_info["status"] == "ACTIVE_CLASS" else None

    # 2. Bulk fetch all relevant TimetableEntries for the day in ONE query
    day_entries = list(TimetableEntry.objects.filter(
        semester=sem_obj,
        day=day_code
    ).select_related(
        'subject', 'teacher', 'room', 'section', 'group', 'merge_group', 'time_slot'
    ).prefetch_related(
        'merge_group__groups'
    ))

    # 3. Bulk fetch all Overrides for the date in ONE query
    day_overrides = list(TimetableOverride.objects.filter(
        date=curr_date,
        semester=sem_obj
    ).select_related('subject', 'teacher', 'room', 'section'))

    # 4. Bulk fetch Cancellations for date in ONE query
    cancellations_set = set(ClassCancellation.objects.filter(
        date=curr_date,
        timetable_entry__semester=sem_obj
    ).values_list('timetable_entry_id', flat=True))

    schedule = []
    for slot in time_slots:
        p_num = slot.period

        # In-memory resolution for slot
        override = next((o for o in day_overrides if o.period == p_num and (o.section_id == sec_obj.id or o.section_id is None)), None)

        entry = None
        if not override:
            period_entries = [e for e in day_entries if e.period == p_num]
            if grp_obj:
                entry = next((e for e in period_entries if e.section_id == sec_obj.id and e.group_id == grp_obj.id), None)
                if not entry:
                    entry = next((e for e in period_entries if e.section_id == sec_obj.id and e.group_id is None and e.merge_group_id is None), None)
            else:
                entry = next((e for e in period_entries if e.section_id == sec_obj.id and e.merge_group_id is None), None)

            if not entry:
                for me in period_entries:
                    if me.merge_group:
                        if grp_obj and any(g.id == grp_obj.id for g in me.merge_group.groups.all()):
                            entry = me
                            break
                        elif not grp_obj and any(g.section_id == sec_obj.id for g in me.merge_group.groups.all()):
                            entry = me
                            break

        is_cancelled = (entry.id in cancellations_set) if entry else False

        item_status = "FREE"
        if active_p_num and p_num < active_p_num:
            item_status = "COMPLETED"
        elif active_p_num and p_num == active_p_num:
            item_status = "CURRENT"
        elif active_p_num and p_num > active_p_num:
            item_status = "UPCOMING"
        elif curr_period_info["status"] == "AFTER_LAST_PERIOD":
            item_status = "COMPLETED"
        elif curr_period_info["status"] == "BEFORE_FIRST_PERIOD":
            item_status = "UPCOMING"

        if is_cancelled:
            item_status = "CANCELLED"

        sub_code = None
        teacher_name = None
        room_no = None
        class_type = None

        if override:
            sub_code = override.subject.code
            teacher_name = override.teacher.full_name
            room_no = override.room.room_number
            class_type = override.get_class_type_display()
        elif entry:
            sub_code = entry.subject.code
            teacher_name = entry.teacher.full_name if entry.teacher else None
            room_no = entry.room.room_number if entry.room else None
            class_type = entry.get_class_type_display()

        schedule.append({
            "period": p_num,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
            "subject": sub_code,
            "teacher": teacher_name,
            "room": room_no,
            "class_type": class_type,
            "status": item_status,
        })
    if order and str(order).lower() in ("desc", "reverse"):
        schedule.reverse()

    return schedule
