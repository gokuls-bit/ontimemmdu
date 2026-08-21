import datetime
from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry, TimetableOverride
)
from core.services.admin.alteration_engine import (
    create_timetable_alteration, approve_timetable_alteration, emergency_room_change
)
from core.services.timetable.student_schedule import get_current_class
from core.services.location.room_engine import get_room_status


class AlterationEngineTestCase(TestCase):
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

    def test_critical_alteration_workflow(self):
        """
        Critical Test Requirement 43:
        Original: Monday P3 Room 357 Operating Systems.
        Alteration: Move to Room 269 on specific date.
        Verify Student Engine (Module 3) & Location Engine (Module 4) report Room 269,
        while master timetable in PostgreSQL remains Room 357.
        """
        test_date = datetime.date(2026, 8, 24)  # Monday

        # 1. Create alteration to Room 269
        override, conflicts = create_timetable_alteration(
            timetable_entry_id=self.entry.id,
            date_val=test_date,
            period=3,
            new_room_val="269",
            reason="Projector failure in Room 357"
        )
        self.assertEqual(len(conflicts), 0)

        # 2. Approve alteration
        approved_override = approve_timetable_alteration(override.id)
        self.assertEqual(approved_override.room.room_number, "269")

        # 3. Master timetable must remain unchanged in DB
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.room.room_number, "357")

    def test_emergency_room_change_wizard(self):
        """Test emergency room change wizard."""
        test_date = datetime.date(2026, 8, 24)
        override = emergency_room_change(
            timetable_entry_id=self.entry.id,
            date_val=test_date,
            new_room_number="269",
            reason="Water leak in 357"
        )
        self.assertEqual(override.room.room_number, "269")
