import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from timetable.models import Semester, Section, Subject, Teacher, Room, TimeSlot, TimetableEntry
from core.services.admin.maintenance_engine import create_room_maintenance, create_room_reservation
from core.services.admin.alteration_engine import create_timetable_alteration


class RoomMaintenanceTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.room269 = Room.objects.create(room_number="269", capacity=70)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        self.entry = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p3
        )

    def test_room_maintenance_blocks_alterations(self):
        """
        Critical Test Requirement 45:
        Set Room 269 under MAINTENANCE.
        Attempt alteration into Room 269 -> Verify conflict detected and reported.
        """
        test_date = datetime.date(2026, 8, 24)
        create_room_maintenance(
            room_number="269",
            date_val=test_date,
            reason="AC repair"
        )

        override, conflicts = create_timetable_alteration(
            timetable_entry_id=self.entry.id,
            date_val=test_date,
            period=3,
            new_room_val="269",
            reason="Move class"
        )

        self.assertTrue(len(conflicts) > 0)
        self.assertEqual(conflicts[0]['type'], 'ROOM_MAINTENANCE')
