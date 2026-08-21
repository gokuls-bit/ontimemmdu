import datetime
from zoneinfo import ZoneInfo
from django.test import SimpleTestCase
from core.services.timetable.clock import get_current_datetime, KOLKATA_TZ


class ClockTestCase(SimpleTestCase):
    def test_default_current_datetime_is_aware(self):
        """Verify get_current_datetime returns aware datetime in Asia/Kolkata."""
        dt = get_current_datetime()
        self.assertIsNotNone(dt.tzinfo)
        self.assertEqual(dt.tzname(), "IST")  # Asia/Kolkata standard time is IST

    def test_naive_datetime_conversion(self):
        """Verify naive datetime input is localized to Asia/Kolkata."""
        naive_dt = datetime.datetime(2026, 8, 21, 10, 40, 0)
        aware_dt = get_current_datetime(naive_dt)
        self.assertIsNotNone(aware_dt.tzinfo)
        self.assertEqual(aware_dt.hour, 10)
        self.assertEqual(aware_dt.minute, 40)
        self.assertEqual(aware_dt.tzinfo, KOLKATA_TZ)

    def test_aware_datetime_conversion(self):
        """Verify aware datetime in UTC is converted to Asia/Kolkata (UTC +05:30)."""
        utc_dt = datetime.datetime(2026, 8, 21, 5, 10, 0, tzinfo=datetime.timezone.utc)
        kolkata_dt = get_current_datetime(utc_dt)
        self.assertEqual(kolkata_dt.hour, 10)
        self.assertEqual(kolkata_dt.minute, 40)
        self.assertEqual(kolkata_dt.tzinfo, KOLKATA_TZ)

    def test_invalid_type_raises_type_error(self):
        """Verify non-datetime argument raises TypeError."""
        with self.assertRaises(TypeError):
            get_current_datetime("2026-08-21 10:40:00")
