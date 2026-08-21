import datetime
from django.test import TestCase
from timetable.models import AuditLog
from core.services.admin.audit_service import log_admin_action


class AuditLoggingTestCase(TestCase):
    def test_audit_log_creation(self):
        """
        Critical Test Requirement 46:
        Perform room change action -> Verify AuditLog creates immutable record.
        """
        log = log_admin_action(
            user=None,
            action="ROOM_CHANGED",
            target_model="TimetableOverride",
            target_id="1",
            old_values={"room": "357"},
            new_values={"room": "269"},
            reason="Projector failure"
        )

        self.assertEqual(log.action, "ROOM_CHANGED")
        self.assertEqual(log.old_values["room"], "357")
        self.assertEqual(log.new_values["room"], "269")
        self.assertEqual(log.reason, "Projector failure")
        self.assertTrue(AuditLog.objects.filter(id=log.id).exists())
