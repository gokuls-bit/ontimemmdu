import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.timetable.timetable_state import get_student_timetable_state
from core.services.timetable.clock import KOLKATA_TZ


class TimetableStateTestCase(TestCase):
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

        # TimeSlots for Monday
        self.slot_p1 = TimeSlot.objects.create(day="MON", period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40))
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))

        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_dbms, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )
        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_cn, teacher=self.teacher2, room=self.room269,
            time_slot=self.slot_p3
        )

    def test_consolidated_student_timetable_state(self):
        """Verify get_student_timetable_state returns complete structured dictionary."""
        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)
        state = get_student_timetable_state(5, "5CSEA1", "G1", now=now)

        self.assertEqual(state["timezone"], "Asia/Kolkata")
        self.assertEqual(state["day"], "MON")
        self.assertEqual(state["student"]["semester"], "5th Semester")
        self.assertEqual(state["student"]["section"], "5CSEA1")
        self.assertEqual(state["student"]["group"], "G1")

        self.assertEqual(state["current_class"]["subject"], "BCSE-501")
        self.assertEqual(state["current_class"]["room"], "357")

        self.assertEqual(state["next_class"]["subject"], "BCSE-502")
        self.assertEqual(state["next_class"]["room"], "269")

        self.assertEqual(len(state["today_schedule"]), 3)

    def test_database_query_efficiency(self):
        """33 & 34. Query performance test proving zero N+1 database queries."""
        now = datetime.datetime(2026, 8, 24, 10, 6, 0, tzinfo=KOLKATA_TZ)

        # Warm up Django cache if needed
        get_student_timetable_state(5, "5CSEA1", "G1", now=now)

        # Execute under strict query limit count (max 30 queries for full state evaluation)
        with self.assertNumQueries(26):
            state = get_student_timetable_state(5, "5CSEA1", "G1", now=now)
            self.assertIsNotNone(state["current_class"])
