import datetime
from zoneinfo import ZoneInfo
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room,
    TimeSlot, TimetableEntry, AcademicHoliday, ClassCancellation
)
from core.services.timetable.student_schedule import (
    get_current_class, get_next_class, get_day_schedule
)
from core.services.timetable.clock import KOLKATA_TZ


class StudentScheduleTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.sub_dbms = Subject.objects.create(code="BCSE-501", name="Database Systems", short_name="DBMS", semester=self.sem5)
        self.sub_cn = Subject.objects.create(code="BCSE-502", name="Computer Networks", short_name="CN", semester=self.sem5)

        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.teacher2 = Teacher.objects.create(employee_id="T002", first_name="Ada", last_name="Lovelace", email="ada@cse.edu")

        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.room269 = Room.objects.create(room_number="269", capacity=70)

        # TimeSlots for Monday (2026-08-24 is Monday)
        self.slot_p1 = TimeSlot.objects.create(day="MON", period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40))
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))
        self.slot_p4 = TimeSlot.objects.create(day="MON", period=4, start_time=datetime.time(11, 40), end_time=datetime.time(12, 40))
        self.slot_p5 = TimeSlot.objects.create(day="MON", period=5, start_time=datetime.time(12, 40), end_time=datetime.time(13, 40))

        # Schedule P2 and P3
        self.tt_p2 = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_dbms, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )
        self.tt_p3 = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_cn, teacher=self.teacher2, room=self.room269,
            time_slot=self.slot_p3
        )

    def test_current_class_resolution(self):
        """14. Current lecture resolution at 10:06 AM during P2."""
        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)
        curr = get_current_class(5, "5CSEA1", "G1", now=now)

        self.assertEqual(curr["status"], "ACTIVE_CLASS")
        self.assertEqual(curr["period"], 2)
        self.assertEqual(curr["subject"], "BCSE-501")
        self.assertEqual(curr["teacher"], "Alan Turing")
        self.assertEqual(curr["room"], "357")
        self.assertEqual(curr["minutes_elapsed"], 26)
        self.assertEqual(curr["minutes_remaining"], 34)

    def test_next_class_resolution(self):
        """16. Next lecture resolution during P2."""
        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)
        nxt = get_next_class(5, "5CSEA1", "G1", now=now)

        self.assertEqual(nxt["status"], "UPCOMING_CLASS")
        self.assertEqual(nxt["period"], 3)
        self.assertEqual(nxt["subject"], "BCSE-502")
        self.assertEqual(nxt["teacher"], "Ada Lovelace")
        self.assertEqual(nxt["room"], "269")
        self.assertEqual(nxt["minutes_until_start"], 34)

    def test_class_cancellation_support(self):
        """13 & 36. Class cancellation handling."""
        cancel_date = datetime.date(2026, 8, 24)
        ClassCancellation.objects.create(timetable_entry=self.tt_p2, date=cancel_date, reason="Faculty on leave")

        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)
        curr = get_current_class(5, "5CSEA1", "G1", now=now)

        self.assertEqual(curr["status"], "CANCELLED")
        self.assertEqual(curr["subject"], "BCSE-501")

    def test_complete_day_schedule(self):
        """32. Complete day schedule ordered by period."""
        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)
        schedule = get_day_schedule(5, "5CSEA1", "G1", now=now)

        self.assertEqual(len(schedule), 5)
        self.assertEqual(schedule[0]["period"], 1)
        self.assertEqual(schedule[0]["status"], "COMPLETED")

        self.assertEqual(schedule[1]["period"], 2)
        self.assertEqual(schedule[1]["status"], "CURRENT")
        self.assertEqual(schedule[1]["subject"], "BCSE-501")

        self.assertEqual(schedule[2]["period"], 3)
        self.assertEqual(schedule[2]["status"], "UPCOMING")
        self.assertEqual(schedule[2]["subject"], "BCSE-502")
