from django.db import transaction
from django.core.exceptions import ValidationError
from timetable.models import Room, RoomException, RoomReservation
from core.services.admin.audit_service import log_admin_action
from core.services.location.exceptions import RoomNotFound


@transaction.atomic
def create_room_maintenance(room_number, date_val, reason="Maintenance", exception_type="MAINTENANCE", user=None):
    """
    Creates a room closure/maintenance exception blocking room availability.
    """
    room_obj = Room.objects.filter(room_number__iexact=str(room_number).strip()).first()
    if not room_obj:
        raise RoomNotFound(f"Room '{room_number}' not found.")

    maint = RoomException.objects.create(
        room=room_obj,
        date=date_val,
        reason=reason,
        exception_type=exception_type
    )

    log_admin_action(
        user=user,
        action="ROOM_MAINTENANCE_CREATED",
        target_model="RoomException",
        target_id=maint.id,
        new_values={"room": room_obj.room_number, "date": str(date_val), "reason": reason},
        reason=reason
    )

    return maint


@transaction.atomic
def create_room_reservation(room_number, date_val, start_time, end_time, event_name, reservation_type="SPECIAL_LECTURE", user=None):
    """
    Creates an event or examination room reservation.
    """
    room_obj = Room.objects.filter(room_number__iexact=str(room_number).strip()).first()
    if not room_obj:
        raise RoomNotFound(f"Room '{room_number}' not found.")

    res = RoomReservation.objects.create(
        room=room_obj,
        date=date_val,
        start_time=start_time,
        end_time=end_time,
        event_name=event_name,
        reservation_type=reservation_type,
        reserved_by=user.username if (user and hasattr(user, 'username')) else "ADMIN"
    )

    log_admin_action(
        user=user,
        action="ROOM_RESERVED",
        target_model="RoomReservation",
        target_id=res.id,
        new_values={"room": room_obj.room_number, "date": str(date_val), "event": event_name},
        reason=f"Reserved for {event_name}"
    )

    return res
