import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from timetable.models import (
    TimetableEntry, TimetableOverride, Room, Teacher, RoomException,
    RoomReservation, ClassCancellation, AcademicHoliday
)
from core.services.admin.audit_service import log_admin_action
from core.services.location.exceptions import RoomNotFound, TeacherNotFound, RoomScheduleConflict, TeacherScheduleConflict


def validate_alteration_conflicts(date_val, period, room_obj, teacher_obj, section_obj=None, exclude_override_id=None):
    """
    Validates room, teacher, section, holiday, and maintenance conflicts for a proposed alteration date/period.
    Returns (is_valid, conflicts_list).
    """
    conflicts = []

    # 1. Holiday Check
    if AcademicHoliday.objects.filter(date=date_val, is_active=True).exists():
        conflicts.append({
            "type": "HOLIDAY",
            "message": f"Date {date_val} is marked as an Academic Holiday."
        })

    # 2. Room Maintenance / Closure Check
    maint = RoomException.objects.filter(room=room_obj, date=date_val).first()
    if maint:
        conflicts.append({
            "type": "ROOM_MAINTENANCE",
            "message": f"Room {room_obj.room_number} is closed for {maint.get_exception_type_display()} ({maint.reason})."
        })

    # 3. Room Reservation Check
    res = RoomReservation.objects.filter(room=room_obj, date=date_val).first()
    if res:
        conflicts.append({
            "type": "ROOM_RESERVATION",
            "message": f"Room {room_obj.room_number} is reserved for {res.event_name} ({res.reserved_by})."
        })

    # 4. Room Timetable Occupancy Check on Day of Week
    weekday_str = date_val.strftime('%a').upper()[:3]
    if weekday_str in ['SAT', 'SUN']:
        weekday_str = 'MON'  # Fallback check

    room_occ = TimetableEntry.objects.filter(room=room_obj, day=weekday_str, period=period).first()
    if room_occ:
        # Check if cancelled for this specific date
        cancellation = ClassCancellation.objects.filter(timetable_entry=room_occ, date=date_val).exists()
        if not cancellation:
            conflicts.append({
                "type": "ROOM_OCCUPIED",
                "message": f"Room {room_obj.room_number} is occupied by {room_occ.subject.short_name} ({room_occ.section.name if room_occ.section else ''}) on period {period}."
            })

    # 5. Room Override Conflict Check
    room_overrides = TimetableOverride.objects.filter(room=room_obj, date=date_val, period=period)
    if exclude_override_id:
        room_overrides = room_overrides.exclude(pk=exclude_override_id)
    if room_overrides.exists():
        ov = room_overrides.first()
        conflicts.append({
            "type": "ROOM_OVERRIDE_CONFLICT",
            "message": f"Room {room_obj.room_number} already has an override for {ov.subject.short_name} on {date_val} P{period}."
        })

    # 6. Teacher Conflict Check
    if teacher_obj:
        teach_occ = TimetableEntry.objects.filter(teacher=teacher_obj, day=weekday_str, period=period).first()
        if teach_occ and not ClassCancellation.objects.filter(timetable_entry=teach_occ, date=date_val).exists():
            conflicts.append({
                "type": "TEACHER_CONFLICT",
                "message": f"Teacher {teacher_obj.full_name} is already teaching {teach_occ.subject.short_name} on period {period} in Room {teach_occ.room.room_number}."
            })

    return (len(conflicts) == 0, conflicts)


@transaction.atomic
def create_timetable_alteration(timetable_entry_id, date_val, period, new_room_val, new_teacher_val=None, reason="", user=None):
    """
    Creates a date-specific TimetableOverride without destroying original timetable.
    """
    try:
        entry = TimetableEntry.objects.select_related('semester', 'section', 'group', 'subject', 'teacher', 'room').get(id=timetable_entry_id)
    except TimetableEntry.DoesNotExist:
        raise ValidationError("Original timetable entry not found.")

    room_obj = Room.objects.filter(room_number__iexact=str(new_room_val).strip()).first()
    if not room_obj:
        raise RoomNotFound(f"Target room '{new_room_val}' does not exist.")

    teacher_obj = entry.teacher
    if new_teacher_val:
        t = Teacher.objects.filter(employee_id__iexact=str(new_teacher_val).strip()).first() or \
            Teacher.objects.filter(first_name__icontains=str(new_teacher_val).strip()).first()
        if not t:
            raise TeacherNotFound(f"Faculty '{new_teacher_val}' not found.")
        teacher_obj = t

    is_valid, conflicts = validate_alteration_conflicts(date_val, period, room_obj, teacher_obj, entry.section)

    override = TimetableOverride.objects.create(
        timetable_entry=entry,
        date=date_val,
        period=period,
        semester=entry.semester,
        section=entry.section,
        group=entry.group,
        subject=entry.subject,
        teacher=teacher_obj,
        room=room_obj,
        class_type=entry.class_type,
        reason=reason or "Administrative timetable alteration"
    )

    log_admin_action(
        user=user,
        action="ALTERATION_CREATED",
        target_model="TimetableOverride",
        target_id=override.id,
        old_values={"room": entry.room.room_number, "teacher": entry.teacher.full_name},
        new_values={"room": room_obj.room_number, "teacher": teacher_obj.full_name, "date": str(date_val), "period": period},
        reason=reason
    )

    return override, conflicts


@transaction.atomic
def approve_timetable_alteration(override_id, user=None):
    """
    Atomically re-validates conflicts and approves timetable alteration.
    """
    try:
        override = TimetableOverride.objects.select_for_update().get(id=override_id)
    except TimetableOverride.DoesNotExist:
        raise ValidationError("Timetable override record not found.")

    is_valid, conflicts = validate_alteration_conflicts(
        override.date, override.period, override.room, override.teacher, override.section, exclude_override_id=override.id
    )

    if not is_valid:
        raise ValidationError(f"Cannot approve alteration due to active conflicts: {conflicts[0]['message']}")

    log_admin_action(
        user=user,
        action="ALTERATION_APPROVED",
        target_model="TimetableOverride",
        target_id=override.id,
        new_values={"date": str(override.date), "room": override.room.room_number, "period": override.period},
        reason="Approved by administrator"
    )

    return override


@transaction.atomic
def emergency_room_change(timetable_entry_id, date_val, new_room_number, reason="Emergency room change", user=None):
    """
    Fast emergency room change wizard.
    """
    override, conflicts = create_timetable_alteration(
        timetable_entry_id=timetable_entry_id,
        date_val=date_val,
        period=TimetableEntry.objects.get(id=timetable_entry_id).period,
        new_room_val=new_room_number,
        reason=reason,
        user=user
    )

    approved_override = approve_timetable_alteration(override.id, user=user)
    return approved_override
