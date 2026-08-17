from typing import List, Dict, Tuple, Set, Any
from .parser import ParsedEntry
from .result import ImportResult
from timetable.models import Section, Room, Teacher, Subject, Semester, TimeSlot


VALID_DAYS = {'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'}


def normalize_day(day_str: Any) -> str:
    if not day_str:
        return ""
    d = str(day_str).strip().upper()
    mapping = {
        'MON': 'MON', 'MONDAY': 'MON',
        'TUE': 'TUE', 'TUESDAY': 'TUE',
        'WED': 'WED', 'WEDNESDAY': 'WED',
        'THU': 'THU', 'THURSDAY': 'THU',
        'FRI': 'FRI', 'FR I DAY': 'FRI', 'FRIDAY': 'FRI',
        'SAT': 'SAT', 'SATURDAY': 'SAT',
        'SUN': 'SUN', 'SUNDAY': 'SUN',
    }
    return mapping.get(d, d[:3])


def validate_parsed_entries(
    entries: List[ParsedEntry],
    result: ImportResult,
    allow_auto_create: bool = True
) -> bool:
    """
    Validates a list of ParsedEntry objects against business rules:
    - Checks for formula cells
    - Checks for missing subject, teacher, room
    - Checks section resolution
    - Checks global duplicate room booking (DUPLICATE_ROOM_BOOKING)
    """
    valid = True
    room_bookings: Dict[Tuple[str, str, int], List[ParsedEntry]] = {}

    for idx, entry in enumerate(entries):
        ctx = entry.context
        sheet = ctx.get('sheet')
        cell = ctx.get('cell')
        row = ctx.get('row')
        col = ctx.get('column')
        sec_code = ctx.get('section')
        day_raw = ctx.get('day')
        period = ctx.get('period')

        # Skip breaks / free periods
        if entry.is_break:
            result.free_periods_count += 1
            continue

        # 1. Formula Cell Check
        if entry.is_formula:
            result.add_error(
                "FORMULA_CELL",
                f"Cell '{cell}' contains an un-evaluated Excel formula. Formulas are strictly prohibited.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False
            continue

        # 2. Day & Period Validation
        norm_day = normalize_day(day_raw)
        if norm_day not in {'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'}:
            result.add_error(
                "INVALID_DAY",
                f"Invalid or missing day identifier '{day_raw}'.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        if not isinstance(period, int) or period < 1 or period > 12:
            result.add_error(
                "INVALID_PERIOD",
                f"Invalid period number '{period}'. Period must be an integer between 1 and 12.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        # 3. Section Validation
        if not sec_code and not entry.merge_group:
            result.add_error(
                "INVALID_SECTION",
                "Timetable entry does not specify a valid section or merge group.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        # 4. Subject Validation
        if not entry.subject_code:
            result.add_error(
                "MISSING_SUBJECT",
                "Timetable entry has no valid subject code.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        # 5. Teacher Validation
        if not entry.teacher:
            result.add_error(
                "MISSING_TEACHER",
                "Timetable entry has no valid teacher assigned.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        # 6. Room Validation
        if not entry.room:
            result.add_error(
                "MISSING_ROOM",
                "Timetable entry has no valid room specified.",
                sheet=sheet, cell=cell, row=row, column=col, section=sec_code,
                day=day_raw, period=period, raw_value=entry.raw
            )
            valid = False

        # Track laboratory & stats
        if entry.class_type == 'LAB':
            result.laboratories_count += 1

        # 7. Global Room Booking Conflict Tracking
        if entry.room and norm_day and period:
            room_key = (entry.room.upper(), norm_day, period)
            if room_key not in room_bookings:
                room_bookings[room_key] = []
            room_bookings[room_key].append(entry)

    # 8. Room Double Booking Validation across entries
    for (room_str, day_code, p_num), booking_list in room_bookings.items():
        if len(booking_list) > 1:
            # Check if all entries sharing the room are part of the SAME merge_group
            merge_names = [b.context.get('section') for b in booking_list]
            merge_groups = [b.merge_group for b in booking_list if b.merge_group]

            # If entries share the same room on the same day/period, check if they are legitimately merged
            is_legitimate_shared = (len(merge_groups) == len(booking_list) and len(merge_groups) > 0)

            if not is_legitimate_shared:
                sec_str = ", ".join(filter(None, set(merge_names))) or "Unknown Sections"
                first = booking_list[0]
                result.add_error(
                    "DUPLICATE_ROOM_BOOKING",
                    f"Room '{room_str}' is double-booked on {day_code} Period {p_num} by multiple independent sections ({sec_str}).",
                    sheet=first.context.get('sheet'),
                    cell=first.context.get('cell'),
                    row=first.context.get('row'),
                    column=first.context.get('column'),
                    section=first.context.get('section'),
                    day=day_code,
                    period=p_num,
                    raw_value=first.raw
                )
                valid = False

    return valid
