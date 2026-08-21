from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, MergeGroup, Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.location.conflict_engine import (
    check_room_schedule_conflict, check_teacher_schedule_conflict
)


class ConflictEngineTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.sec_b = Section.objects.create(name="5CSEB1", semester=self.sem5, capacity=60)

        self.room357 = Room.objects.create(room_number="357", capacity=70)
        self.room269 = Room.objects.create(room_number="269", capacity=70)

        self.sub_os = Subject.objects.create(code="BCSE-501", name="Operating Systems", short_name="OS", semester=self.sem5)
        self.sub_cn = Subject.objects.create(code="BCSE-502", name="Computer Networks", short_name="CN", semester=self.sem5)

        self.teacher1 = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.teacher2 = Teacher.objects.create(employee_id="T002", first_name="Ada", last_name="Lovelace", email="ada@cse.edu")

        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time="09:40", end_time="10:40")

    def test_room_schedule_conflict_detection(self):
        """7 & 19. Room schedule conflict detection."""
        # Use bulk_create to bypass model save clean() for conflict testing
        e1 = TimetableEntry(
            semester=self.sem5, section=self.sec_a, subject=self.sub_os,
            teacher=self.teacher1, room=self.room357, time_slot=self.slot_p2,
            day="MON", period=2, start_time="09:40", end_time="10:40"
        )
        e2 = TimetableEntry(
            semester=self.sem5, section=self.sec_b, subject=self.sub_cn,
            teacher=self.teacher2, room=self.room357, time_slot=self.slot_p2,
            day="MON", period=2, start_time="09:40", end_time="10:40"
        )
        TimetableEntry.objects.bulk_create([e1, e2])

        has_conflict, err_code, entries = check_room_schedule_conflict(self.room357, "MON", 2)
        self.assertTrue(has_conflict)
        self.assertEqual(err_code, "ROOM_SCHEDULE_CONFLICT")
        self.assertEqual(len(entries), 2)

    def test_teacher_schedule_conflict_detection(self):
        """29. Teacher schedule conflict detection."""
        # Use bulk_create to bypass model save clean() for conflict testing
        e1 = TimetableEntry(
            semester=self.sem5, section=self.sec_a, subject=self.sub_os,
            teacher=self.teacher1, room=self.room357, time_slot=self.slot_p2,
            day="MON", period=2, start_time="09:40", end_time="10:40"
        )
        e2 = TimetableEntry(
            semester=self.sem5, section=self.sec_b, subject=self.sub_cn,
            teacher=self.teacher1, room=self.room269, time_slot=self.slot_p2,
            day="MON", period=2, start_time="09:40", end_time="10:40"
        )
        TimetableEntry.objects.bulk_create([e1, e2])

        has_conflict, err_code, entries = check_teacher_schedule_conflict(self.teacher1, "MON", 2)
        self.assertTrue(has_conflict)
        self.assertEqual(err_code, "TEACHER_SCHEDULE_CONFLICT")
        self.assertEqual(len(entries), 2)

    def test_legitimate_merged_class_has_no_conflict(self):
        """5 & 20. Merged class in single room has no conflict."""
        grp_f = Group.objects.create(name="F", section=self.sec_a)
        grp_h = Group.objects.create(name="H", section=self.sec_a)
        mg = MergeGroup.objects.create(name="F+H Merge")
        mg.groups.add(grp_f, grp_h)

        TimetableEntry.objects.create(
            semester=self.sem5, merge_group=mg, subject=self.sub_os,
            teacher=self.teacher1, room=self.room357, time_slot=self.slot_p2
        )

        has_conflict, err_code, entries = check_room_schedule_conflict(self.room357, "MON", 2)
        self.assertFalse(has_conflict)
        self.assertIsNone(err_code)
