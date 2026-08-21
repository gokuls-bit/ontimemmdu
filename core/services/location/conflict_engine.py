from typing import Tuple, List, Optional
from timetable.models import TimetableEntry, Room, Teacher
from .exceptions import RoomScheduleConflict, TeacherScheduleConflict


def check_room_schedule_conflict(room: Room, day: str, period: int) -> Tuple[bool, Optional[str], List[TimetableEntry]]:
    """
    Checks if a room has conflicting timetable entries during a specific day and period.
    
    Returns: (has_conflict, error_code, list_of_conflicting_entries)
    """
    entries = list(TimetableEntry.objects.filter(
        room=room,
        day=day,
        period=period
    ).select_related('section', 'group', 'merge_group', 'subject', 'teacher'))

    if len(entries) <= 1:
        return False, None, entries

    # Multiple entries exist: check if they are legitimately merged
    merge_groups = {e.merge_group_id for e in entries if e.merge_group_id is not None}
    if len(merge_groups) == 1 and len([e for e in entries if e.merge_group_id is None]) == 0:
        # Legitimate shared merged class
        return False, None, entries

    return True, "ROOM_SCHEDULE_CONFLICT", entries


def check_teacher_schedule_conflict(teacher: Teacher, day: str, period: int) -> Tuple[bool, Optional[str], List[TimetableEntry]]:
    """
    Checks if a teacher is double-booked across different rooms during a specific day and period.
    
    Returns: (has_conflict, error_code, list_of_conflicting_entries)
    """
    entries = list(TimetableEntry.objects.filter(
        teacher=teacher,
        day=day,
        period=period
    ).select_related('room', 'subject', 'section', 'group', 'merge_group'))

    if len(entries) <= 1:
        return False, None, entries

    rooms = {e.room_id for e in entries}
    if len(rooms) > 1:
        return True, "TEACHER_SCHEDULE_CONFLICT", entries

    return False, None, entries
