import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, MergeGroup, Subject, Teacher, Room, TimeSlot,
    TimetableEntry, TimetableOverride, ClassCancellation, RoomReservation, RoomException
)
from core.services.location.room_engine import (
    get_room_status, search_rooms, get_room_day_schedule,
    get_room_next_free, get_room_next_class, get_room_utilization
)
from core.services.location.exceptions import RoomNotFound
from core.services.timetable.clock import KOLKATA_TZ


class RoomEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.sec_b = Section.objects.create(name="5CSEB1", semester=self.sem5, capacity=60)
        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)

        self.room357 = Room.objects.create(room_number="357", building="Block C", floor=3, room_type="LECTURE_HALL", capacity=70)
        self.room269 = Room.objects.create(room_number="269", building="Block C", floor=2, room_type="LECTURE_HALL", capacity=70)
        self.room_lab1 = Room.objects.create(room_number="Lab-1", building="Block C", floor=1, room_type="LAB", capacity=35)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.sub_cn = Subject.objects.create(code="BCSE-502", name="Computer Networks", short_name="CN", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")

        # TimeSlots for Monday (2026-08-24 is Monday)
        self.slot_p1 = TimeSlot.objects.create(day="MON", period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40))
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))
        self.slot_p4 = TimeSlot.objects.create(day="MON", period=4, start_time=datetime.time(11, 40), end_time=datetime.time(12, 40))

        # Schedule P2 and P3 in Room 357
        self.tt_p2 = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p2
        )
        self.tt_p3 = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_b,
            subject=self.sub_cn, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p3
        )

    def test_occupied_room_status(self):
        """1. Occupied room status at 10:20 AM during P2."""
        now = datetime.datetime(2026, 8, 24, 10, 20, 0, tzinfo=KOLKATA_TZ)
        status = get_room_status("357", now=now)

        self.assertEqual(status["status"], "OCCUPIED")
        self.assertEqual(status["current_class"]["subject"], "BCSE-501")
        self.assertEqual(status["current_class"]["teacher"], "Alan Turing")
        self.assertEqual(status["current_class"]["section"], "5CSEA1")
        self.assertEqual(status["minutes_remaining"], 20)

    def test_free_room_status(self):
        """2. Free room status at 10:20 AM for Room 269."""
        now = datetime.datetime(2026, 8, 24, 10, 20, 0, tzinfo=KOLKATA_TZ)
        status = get_room_status("269", now=now)

        self.assertEqual(status["status"], "FREE")
        self.assertIsNone(status["current_class"])

    def test_unknown_room_raises_error(self):
        """3. Unknown room number raises RoomNotFound."""
        with self.assertRaises(RoomNotFound):
            get_room_status("9999")

    def test_room_next_free_continuous_occupation(self):
        """8. Continuous P2->P3 occupation returns end of P3 (11:40)."""
        now = datetime.datetime(2026, 8, 24, 10, 0, 0, tzinfo=KOLKATA_TZ)
        nxt_free = get_room_next_free("357", now=now)

        self.assertEqual(nxt_free["status"], "OCCUPIED")
        self.assertEqual(nxt_free["next_free_time"], "11:40")

    def test_room_reservation_takes_precedence(self):
        """13. RoomReservation returns RESERVED status."""
        r_date = datetime.date(2026, 8, 24)
        RoomReservation.objects.create(
            room=self.room269, date=r_date, start_time=datetime.time(10, 0),
            end_time=datetime.time(12, 0), event_name="Mid-Term Exam", reserved_by="Exam Dept"
        )
        now = datetime.datetime(2026, 8, 24, 10, 30, 0, tzinfo=KOLKATA_TZ)
        status = get_room_status("269", now=now)

        self.assertEqual(status["status"], "RESERVED")
        self.assertEqual(status["event_name"], "Mid-Term Exam")

    def test_room_maintenance_exception(self):
        """12. RoomException returns MAINTENANCE status."""
        r_date = datetime.date(2026, 8, 24)
        RoomException.objects.create(
            room=self.room269, date=r_date, reason="AC Repair", exception_type="MAINTENANCE"
        )
        now = datetime.datetime(2026, 8, 24, 10, 30, 0, tzinfo=KOLKATA_TZ)
        status = get_room_status("269", now=now)

        self.assertEqual(status["status"], "MAINTENANCE")

    def test_search_rooms(self):
        """Room ORM search."""
        results = search_rooms("357")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["room_number"], "357")
