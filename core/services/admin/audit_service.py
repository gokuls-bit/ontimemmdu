from timetable.models import AuditLog


def log_admin_action(user, action, target_model, target_id="", old_values=None, new_values=None, reason="", ip_address=None):
    """
    Records an append-only audit entry for administrative actions.
    """
    user_id_str = user.username if (user and hasattr(user, 'username')) else (str(user) if user else "SYSTEM_ADMIN")
    user_obj = user if (user and hasattr(user, 'pk') and user.pk) else None

    return AuditLog.objects.create(
        user=user_obj,
        user_identifier=user_id_str,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        old_values=old_values or {},
        new_values=new_values or {},
        reason=reason or "",
        ip_address=ip_address
    )
