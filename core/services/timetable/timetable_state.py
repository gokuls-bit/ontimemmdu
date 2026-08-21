import datetime
from typing import Optional, Dict, Any
from .clock import get_current_datetime
from .period_engine import get_current_period
from .student_schedule import get_current_class, get_next_class, get_day_schedule
from .group_resolver import validate_student_context


def get_student_timetable_state(
    semester_val: Any,
    section_val: Any,
    group_val: Optional[Any] = None,
    now: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    """
    Primary service function returning complete real-time timetable decision state for a student.
    
    Consolidates server time, student context, current period status, current class,
    next class, and complete day schedule.
    """
    sem_obj, sec_obj, grp_obj = validate_student_context(semester_val, section_val, group_val)
    dt = get_current_datetime(now)
    period_info = get_current_period(dt)

    current_class_info = get_current_class(sem_obj, sec_obj, grp_obj, dt)
    next_class_info = get_next_class(sem_obj, sec_obj, grp_obj, dt)
    day_schedule_info = get_day_schedule(sem_obj, sec_obj, grp_obj, now=dt)

    overall_status = current_class_info.get("status") or period_info.get("status")

    return {
        "server_time": dt.isoformat(),
        "timezone": "Asia/Kolkata",
        "date": dt.date().isoformat(),
        "day": period_info["day"],
        "day_name": period_info["day_name"],
        "status": overall_status,
        "student": {
            "semester": f"{sem_obj.number}th Semester",
            "section": sec_obj.name,
            "group": grp_obj.name if grp_obj else None,
        },
        "current_period": period_info,
        "current_class": current_class_info,
        "next_class": next_class_info,
        "today_schedule": day_schedule_info,
    }
