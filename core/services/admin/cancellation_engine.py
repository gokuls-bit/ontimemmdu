from django.db import transaction
from django.core.exceptions import ValidationError
from timetable.models import TimetableEntry, ClassCancellation
from core.services.admin.audit_service import log_admin_action


@transaction.atomic
def cancel_class_instance(timetable_entry_id, date_val, reason="", user=None):
    """
    Cancels a single class instance on a specific date while keeping master timetable intact.
    """
    try:
        entry = TimetableEntry.objects.select_related('subject', 'teacher', 'room', 'section').get(id=timetable_entry_id)
    except TimetableEntry.DoesNotExist:
        raise ValidationError("Timetable entry not found.")

    cancellation, created = ClassCancellation.objects.get_or_create(
        timetable_entry=entry,
        date=date_val,
        defaults={
            "reason": reason or "Faculty unavailable",
            "cancelled_by": user.username if (user and hasattr(user, 'username')) else "ADMIN"
        }
    )

    log_admin_action(
        user=user,
        action="CLASS_CANCELLED",
        target_model="ClassCancellation",
        target_id=cancellation.id,
        old_values={"subject": entry.subject.short_name, "room": entry.room.room_number},
        new_values={"date": str(date_val), "reason": cancellation.reason},
        reason=reason
    )

    return cancellation
