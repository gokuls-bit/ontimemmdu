import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.location.availability_engine import (
    get_free_rooms, get_room_availability, find_available_rooms
)
from core.services.timetable.clock import KOLKATA_TZ


class AvailabilityEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.room101 = Room.objects.create(room_number="101", room_type="LECTURE_HALL", capacity=70)
        self.room102 = Room.objects.create(room_number="102", room_type="LECTURE_HALL", capacity=70)
        self.room_lab1 = Room.objects.create(room_number="Lab-1", room_type="LAB", capacity=35)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")

        # P3: 10:40 - 11:40, P4: 11:40 - 12:40, P5: 12:40 - 13:40
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))
        self.slot_p4 = TimeSlot.objects.create(day="MON", period=4, start_time=datetime.time(11, 40), end_time=datetime.time(12, 40))
        self.slot_p5 = TimeSlot.objects.create(day="MON", period=5, start_time=datetime.time(12, 40), end_time=datetime.time(13, 40))

        # Room 101 occupied P4 (11:40 - 12:40)
        TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_os, teacher=self.teacher1, room=self.room101,
            time_slot=self.slot_p4
        )

    def test_get_free_rooms(self):
        """32 & 37. Get free rooms at 10:50 AM."""
        now = datetime.datetime(2026, 8, 24, 10, 50, 0, tzinfo=KOLKATA_TZ)
        free = get_free_rooms(now=now)

        self.assertEqual(len(free), 3)

    def test_find_available_rooms_complete_interval_rejection(self):
        """38. Complete requested interval availability (11:00 - 13:00).
        Room 101 is occupied 11:40 - 12:40, so it must NOT be returned.
        Room 102 and Lab-1 are free 11:00 - 13:00, so they MUST be returned.
        """
        r_date = datetime.date(2026, 8, 24)
        avail = find_available_rooms(start_time="11:00", end_time="13:00", date_val=r_date)

        avail_numbers = [r["room"] for r in avail]
        self.assertNotIn("101", avail_numbers)
        self.assertIn("102", avail_numbers)
        self.assertIn("Lab-1", avail_numbers)

    def test_find_available_rooms_room_type_filter(self):
        """36 & 37. Filter available rooms by room_type="LAB"."""
        r_date = datetime.date(2026, 8, 24)
        avail_labs = find_available_rooms(start_time="11:00", end_time="13:00", room_type="LAB", date_val=r_date)

        self.assertEqual(len(avail_labs), 1)
        self.assertEqual(avail_labs[0]["room"], "Lab-1")
