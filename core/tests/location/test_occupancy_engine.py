import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.location.occupancy_engine import (
    get_all_room_statuses, get_occupied_rooms, get_campus_occupancy_state,
    get_location_intelligence_state
)
from core.services.timetable.clock import KOLKATA_TZ


class OccupancyEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.room1 = Room.objects.create(room_number="101", room_type="LECTURE_HALL", capacity=70)
        self.room2 = Room.objects.create(room_number="102", room_type="LECTURE_HALL", capacity=70)
        self.room3 = Room.objects.create(room_number="Lab-1", room_type="LAB", capacity=35)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")

        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_os, teacher=self.teacher1, room=self.room1,
            time_slot=self.slot_p2
        )

    def test_get_all_room_statuses(self):
        """31 & 32. Get all room statuses."""
        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        statuses = get_all_room_statuses(now=now)

        self.assertEqual(len(statuses), 3)

    def test_get_occupied_rooms(self):
        """Get occupied rooms."""
        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        occ = get_occupied_rooms(now=now)

        self.assertEqual(len(occ), 1)
        self.assertEqual(occ[0]["room"], "101")

    def test_campus_occupancy_state(self):
        """33, 34, 35. Campus occupancy state calculations."""
        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        campus = get_campus_occupancy_state(now=now)

        self.assertEqual(campus["total_rooms"], 3)
        self.assertEqual(campus["occupied_rooms"], 1)
        self.assertEqual(campus["free_rooms"], 2)
        self.assertEqual(campus["active_classes"], 1)
        self.assertEqual(campus["active_teachers"], 1)
        self.assertEqual(campus["utilization_percentage"], 33.33)

    def test_location_intelligence_state(self):
        """Combined location intelligence payload."""
        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        state = get_location_intelligence_state(room_val="101", teacher_val="T001", now=now)

        self.assertIsNotNone(state["room_status"])
        self.assertIsNotNone(state["teacher_status"])
        self.assertIsNotNone(state["campus_occupancy"])
