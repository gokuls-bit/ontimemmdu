import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.location.teacher_engine import (
    get_teacher_current_location, search_teachers, get_teacher_day_schedule,
    get_teacher_next_class, get_all_teacher_statuses
)
from core.services.location.exceptions import TeacherNotFound
from core.services.timetable.clock import KOLKATA_TZ


class TeacherEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)

        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.teacher2 = Teacher.objects.create(employee_id="T002", first_name="Ada", last_name="Lovelace", email="ada@cse.edu")

        self.slot_p1 = TimeSlot.objects.create(day="MON", period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40))
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )

    def test_teacher_currently_teaching(self):
        """21 & 32. Teacher currently teaching at 10:20 AM."""
        now = datetime.datetime(2026, 8, 24, 10, 20, 0, tzinfo=KOLKATA_TZ)
        loc = get_teacher_current_location("T001", now=now)

        self.assertEqual(loc["status"], "TEACHING")
        self.assertEqual(loc["room"], "357")
        self.assertEqual(loc["subject"], "BCSE-501")
        self.assertEqual(loc["section"], "5CSEA1")
        self.assertEqual(loc["minutes_remaining"], 20)

    def test_teacher_currently_free(self):
        """22. Teacher currently free."""
        now = datetime.datetime(2026, 8, 24, 10, 20, 0, tzinfo=KOLKATA_TZ)
        loc = get_teacher_current_location("T002", now=now)

        self.assertEqual(loc["status"], "FREE")
        self.assertIsNone(loc["room"])

    def test_search_teachers(self):
        """30. Teacher search by name or employee ID."""
        results = search_teachers("Turing")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["employee_id"], "T001")

    def test_teacher_not_found_raises_error(self):
        """TeacherNotFound error for invalid ID."""
        with self.assertRaises(TeacherNotFound):
            get_teacher_current_location("INVALID_ID")
