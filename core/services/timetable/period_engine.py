import datetime
from typing import Optional, Dict, Any, List
from .clock import get_current_datetime
from timetable.models import TimeSlot, AcademicHoliday

DAY_MAP = {
    0: ('MON', 'Monday'),
    1: ('TUE', 'Tuesday'),
    2: ('WED', 'Wednesday'),
    3: ('THU', 'Thursday'),
    4: ('FRI', 'Friday'),
    5: ('SAT', 'Saturday'),
    6: ('SUN', 'Sunday'),
}


def get_current_period(now: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Determines current period status for authoritative server time.
    
    Interval convention: start <= current_time < end.
    At exactly 10:40:00 (where P2 ends at 10:40 and P3 starts at 10:40), 10:40:00 is assigned to P3.
    """
    dt = get_current_datetime(now)
    curr_date = dt.date()
    curr_time = dt.time()

    day_code, day_name = DAY_MAP[dt.weekday()]

    base_result = {
        "status": "UNKNOWN",
        "date": curr_date.isoformat(),
        "day": day_code,
        "day_name": day_name,
        "period": None,
        "start_time": None,
        "end_time": None,
        "current_time": curr_time.strftime("%H:%M"),
        "elapsed_minutes": 0,
        "remaining_minutes": 0,
        "holiday_name": None,
    }

    # 1. Check Holiday Calendar
    holiday = AcademicHoliday.objects.filter(date=curr_date, is_active=True).first()
    if holiday:
        base_result["status"] = "HOLIDAY"
        base_result["holiday_name"] = holiday.name
        return base_result

    # 2. Check TimeSlots for the day
    time_slots = list(TimeSlot.objects.filter(day=day_code).order_by('period'))

    if not time_slots:
        # Weekend or no period configuration for day
        if day_code in {'SAT', 'SUN'}:
            base_result["status"] = "WEEKEND"
        else:
            base_result["status"] = "NO_CONFIGURED_PERIODS"
        return base_result

    first_slot = time_slots[0]
    last_slot = time_slots[-1]

    # 3. Before First Period
    if curr_time < first_slot.start_time:
        dt_first_start = datetime.datetime.combine(curr_date, first_slot.start_time, tzinfo=dt.tzinfo)
        rem_sec = (dt_first_start - dt).total_seconds()
        base_result["status"] = "BEFORE_FIRST_PERIOD"
        base_result["remaining_minutes"] = int(rem_sec // 60)
        return base_result

    # 4. After Last Period
    if curr_time >= last_slot.end_time:
        base_result["status"] = "AFTER_LAST_PERIOD"
        return base_result

    # 5. Evaluate Period Intervals (start <= curr_time < end)
    active_slot = None
    for slot in time_slots:
        if slot.start_time <= curr_time < slot.end_time:
            active_slot = slot
            break

    if active_slot:
        # Calculate elapsed and remaining minutes
        dt_start = datetime.datetime.combine(curr_date, active_slot.start_time, tzinfo=dt.tzinfo)
        dt_end = datetime.datetime.combine(curr_date, active_slot.end_time, tzinfo=dt.tzinfo)

        elapsed = int((dt - dt_start).total_seconds() // 60)
        remaining = int((dt_end - dt).total_seconds() // 60)

        base_result.update({
            "status": "ACTIVE_CLASS",
            "period": active_slot.period,
            "start_time": active_slot.start_time.strftime("%H:%M"),
            "end_time": active_slot.end_time.strftime("%H:%M"),
            "elapsed_minutes": max(0, elapsed),
            "remaining_minutes": max(0, remaining),
        })
        return base_result

    # 6. Between Periods (Gap between period end and next period start)
    for i in range(len(time_slots) - 1):
        slot_curr = time_slots[i]
        slot_next = time_slots[i + 1]
        if slot_curr.end_time <= curr_time < slot_next.start_time:
            dt_next_start = datetime.datetime.combine(curr_date, slot_next.start_time, tzinfo=dt.tzinfo)
            rem_gap = int((dt_next_start - dt).total_seconds() // 60)

            base_result.update({
                "status": "BETWEEN_PERIODS",
                "period": slot_curr.period,
                "remaining_minutes": max(0, rem_gap),
            })
            return base_result

    return base_result
