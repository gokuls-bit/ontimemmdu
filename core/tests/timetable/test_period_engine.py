import datetime
from zoneinfo import ZoneInfo
from django.test import TestCase
from timetable.models import TimeSlot, AcademicHoliday
from core.services.timetable.period_engine import get_current_period
from core.services.timetable.clock import KOLKATA_TZ


class PeriodEngineTestCase(TestCase):
    def setUp(self):
        # Configure standard Monday time slots for testing:
        # P1: 08:40 - 09:40
        # P2: 09:40 - 10:40
        # P3: 10:40 - 11:40
        # P4: 11:40 - 12:40
        # P5 (Lunch): 12:40 - 13:40
        # P6: 13:40 - 14:40
        self.p1 = TimeSlot.objects.create(day='MON', period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40))
        self.p2 = TimeSlot.objects.create(day='MON', period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))
        self.p3 = TimeSlot.objects.create(day='MON', period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))
        self.p4 = TimeSlot.objects.create(day='MON', period=4, start_time=datetime.time(11, 40), end_time=datetime.time(12, 40))
        self.p5 = TimeSlot.objects.create(day='MON', period=5, start_time=datetime.time(12, 40), end_time=datetime.time(13, 40))

    def test_before_first_period(self):
        """1. Before first period: 08:00 AM on Monday."""
        now = datetime.datetime(2026, 8, 24, 8, 0, 0, tzinfo=KOLKATA_TZ)  # 2026-08-24 is Monday
        res = get_current_period(now)
        self.assertEqual(res["status"], "BEFORE_FIRST_PERIOD")
        self.assertEqual(res["remaining_minutes"], 40)

    def test_exactly_first_period_start(self):
        """2. Exactly first period start: 08:40:00."""
        now = datetime.datetime(2026, 8, 24, 8, 40, 0, tzinfo=KOLKATA_TZ)
        res = get_current_period(now)
        self.assertEqual(res["status"], "ACTIVE_CLASS")
        self.assertEqual(res["period"], 1)
        self.assertEqual(res["elapsed_minutes"], 0)
        self.assertEqual(res["remaining_minutes"], 60)

    def test_during_first_period(self):
        """3. During first period: 09:10 AM."""
        now = datetime.datetime(2026, 8, 24, 9, 10, 0, tzinfo=KOLKATA_TZ)
        res = get_current_period(now)
        self.assertEqual(res["status"], "ACTIVE_CLASS")
        self.assertEqual(res["period"], 1)
        self.assertEqual(res["elapsed_minutes"], 30)
        self.assertEqual(res["remaining_minutes"], 30)

    def test_exact_10_40_00_boundary_convention(self):
        """6 & 26. Exact 10:40:00 boundary convention: start <= now < end.
        P2 ends at 10:40:00, P3 begins at 10:40:00.
        10:39:59 must belong to P2.
        10:40:00 must belong to P3.
        """
        # At 10:39:59 -> P2
        now_p2 = datetime.datetime(2026, 8, 24, 10, 39, 59, tzinfo=KOLKATA_TZ)
        res_p2 = get_current_period(now_p2)
        self.assertEqual(res_p2["status"], "ACTIVE_CLASS")
        self.assertEqual(res_p2["period"], 2)

        # At 10:40:00 -> P3
        now_p3 = datetime.datetime(2026, 8, 24, 10, 40, 0, tzinfo=KOLKATA_TZ)
        res_p3 = get_current_period(now_p3)
        self.assertEqual(res_p3["status"], "ACTIVE_CLASS")
        self.assertEqual(res_p3["period"], 3)
        self.assertEqual(res_p3["elapsed_minutes"], 0)

    def test_after_last_period(self):
        """9. After final period: 14:00 (2:00 PM)."""
        now = datetime.datetime(2026, 8, 24, 14, 0, 0, tzinfo=KOLKATA_TZ)
        res = get_current_period(now)
        self.assertEqual(res["status"], "AFTER_LAST_PERIOD")

    def test_saturday_weekend_check(self):
        """10 & 11. Saturday / Sunday weekend check."""
        now_sat = datetime.datetime(2026, 8, 22, 10, 0, 0, tzinfo=KOLKATA_TZ)  # Saturday
        res = get_current_period(now_sat)
        self.assertEqual(res["status"], "WEEKEND")

    def test_configured_holiday_check(self):
        """12. Configured academic holiday check."""
        holiday_date = datetime.date(2026, 8, 24)
        AcademicHoliday.objects.create(date=holiday_date, name="Independence Celebration Day")

        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        res = get_current_period(now)
        self.assertEqual(res["status"], "HOLIDAY")
        self.assertEqual(res["holiday_name"], "Independence Celebration Day")
