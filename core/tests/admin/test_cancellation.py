import datetime
from django.test import TestCase
from timetable.models import Semester, Section, Subject, Teacher, Room, TimeSlot, TimetableEntry, ClassCancellation
from core.services.admin.cancellation_engine import cancel_class_instance


class CancellationEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.slot_p3 = TimeSlot.objects.create(day="MON", period=3, start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))

        self.entry = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a,
            subject=self.sub_os, teacher=self.teacher1, room=self.room357,
            time_slot=self.slot_p3
        )

    def test_class_cancellation_workflow(self):
        """
        Critical Test Requirement 44:
        Cancel class instance for a specific date.
        Verify cancellation record is created while original timetable remains unchanged.
        """
        test_date = datetime.date(2026, 8, 24)
        cancellation = cancel_class_instance(
            timetable_entry_id=self.entry.id,
            date_val=test_date,
            reason="Faculty attending conference"
        )
        self.assertEqual(cancellation.timetable_entry, self.entry)
        self.assertEqual(cancellation.date, test_date)

        # Master timetable entry is preserved
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.room.room_number, "357")
