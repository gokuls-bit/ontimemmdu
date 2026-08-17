import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from timetable.models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)


class ModelTestCase(TestCase):
    def setUp(self):
        # 1. Semesters
        self.sem1 = Semester.objects.create(number=1, academic_year="2025-2026")
        self.sem3 = Semester.objects.create(number=3, academic_year="2025-2026")

        # 2. Sections
        self.sec_a = Section.objects.create(name="CSE-A", semester=self.sem1, capacity=60)
        self.sec_b = Section.objects.create(name="CSE-B", semester=self.sem1, capacity=60)

        # 3. Groups
        self.group_f = Group.objects.create(name="F", section=self.sec_a)
        self.group_h = Group.objects.create(name="H", section=self.sec_a)
        self.group_j = Group.objects.create(name="J", section=self.sec_b)

        # 4. MergeGroup
        self.merge_fhj = MergeGroup.objects.create(
            name="CSE-F+H+J",
            description="Merged practical session for groups F, H, J"
        )
        self.merge_fhj.groups.add(self.group_f, self.group_h, self.group_j)

        # 5. Subjects
        self.sub_dbms = Subject.objects.create(
            code="CS301",
            name="Database Management Systems",
            short_name="DBMS",
            subject_type=Subject.SubjectType.THEORY,
            credits=4,
            semester=self.sem3
        )
        self.sub_dbms_lab = Subject.objects.create(
            code="CS301P",
            name="Database Management Systems Lab",
            short_name="DBMS Lab",
            subject_type=Subject.SubjectType.LAB,
            credits=2,
            semester=self.sem3
        )

        # 6. Teachers
        self.teacher_1 = Teacher.objects.create(
            employee_id="EMP001",
            first_name="Alan",
            last_name="Turing",
            email="alan.turing@cse.edu",
            designation="Professor"
        )
        self.teacher_2 = Teacher.objects.create(
            employee_id="EMP002",
            first_name="Ada",
            last_name="Lovelace",
            email="ada.lovelace@cse.edu",
            designation="Associate Professor"
        )

        # 7. Rooms
        self.room_c301 = Room.objects.create(
            room_number="C-301",
            building="Engineering Block C",
            floor=3,
            room_type=Room.RoomType.LECTURE_HALL,
            capacity=70
        )
        self.room_lab2 = Room.objects.create(
            room_number="Lab-2",
            building="Engineering Block C",
            floor=2,
            room_type=Room.RoomType.LAB,
            capacity=35
        )

        # 8. TimeSlot
        self.slot_mon_p1 = TimeSlot.objects.create(
            day=TimeSlot.DayChoices.MONDAY,
            period=1,
            start_time=datetime.time(9, 0),
            end_time=datetime.time(10, 0)
        )
        self.slot_mon_p2 = TimeSlot.objects.create(
            day=TimeSlot.DayChoices.MONDAY,
            period=2,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0)
        )

    def test_semester_section_group_creation(self):
        """Verify model creation and string representations."""
        self.assertEqual(str(self.sem1), "Semester 1 (2025-2026)")
        self.assertEqual(str(self.sec_a), "CSE-A (Sem 1)")
        self.assertEqual(str(self.group_f), "CSE-A - Group F")

    def test_unique_constraints(self):
        """Verify unique constraints prevent duplicates."""
        with self.assertRaises(Exception):
            Semester.objects.create(number=1, academic_year="2025-2026")

        with self.assertRaises(Exception):
            Section.objects.create(name="CSE-A", semester=self.sem1)

    def test_room_double_booking_prevention(self):
        """Verify that a room cannot be occupied by multiple entries during the same day and period."""
        # Create first timetable entry
        entry1 = TimetableEntry(
            semester=self.sem3,
            section=self.sec_a,
            subject=self.sub_dbms,
            teacher=self.teacher_1,
            room=self.room_c301,
            time_slot=self.slot_mon_p1,
            class_type=TimetableEntry.ClassType.LECTURE
        )
        entry1.save()

        # Attempt to create second entry in the exact same room, day, period (different section/teacher)
        entry2 = TimetableEntry(
            semester=self.sem3,
            section=self.sec_b,
            subject=self.sub_dbms,
            teacher=self.teacher_2,
            room=self.room_c301,
            time_slot=self.slot_mon_p1,
            class_type=TimetableEntry.ClassType.LECTURE
        )

        with self.assertRaises(ValidationError) as ctx:
            entry2.save()

        self.assertIn("already occupied", str(ctx.exception))

    def test_teacher_double_booking_prevention(self):
        """Verify that a teacher cannot be scheduled in two different rooms at the same time."""
        # Teacher 1 is in C-301 during Monday Period 1
        entry1 = TimetableEntry(
            semester=self.sem3,
            section=self.sec_a,
            subject=self.sub_dbms,
            teacher=self.teacher_1,
            room=self.room_c301,
            time_slot=self.slot_mon_p1,
            class_type=TimetableEntry.ClassType.LECTURE
        )
        entry1.save()

        # Attempt to put Teacher 1 in Lab-2 at the exact same time
        entry2 = TimetableEntry(
            semester=self.sem3,
            section=self.sec_b,
            subject=self.sub_dbms,
            teacher=self.teacher_1,
            room=self.room_lab2,
            time_slot=self.slot_mon_p1,
            class_type=TimetableEntry.ClassType.LECTURE
        )

        with self.assertRaises(ValidationError) as ctx:
            entry2.save()

        self.assertIn("already assigned to a class", str(ctx.exception))

    def test_merged_group_scheduling(self):
        """Verify scheduling a merged group (e.g. F+H+J sharing one class and room)."""
        entry_merge = TimetableEntry(
            semester=self.sem3,
            merge_group=self.merge_fhj,
            subject=self.sub_dbms_lab,
            teacher=self.teacher_2,
            room=self.room_lab2,
            time_slot=self.slot_mon_p2,
            class_type=TimetableEntry.ClassType.LAB
        )
        entry_merge.save()

        self.assertIsNotNone(entry_merge.pk)
        self.assertEqual(entry_merge.merge_group.groups.count(), 3)
        self.assertEqual(entry_merge.day, 'MON')
        self.assertEqual(entry_merge.period, 2)

    def test_missing_target_entity_validation(self):
        """Verify error when neither section nor merge_group is specified."""
        entry_invalid = TimetableEntry(
            semester=self.sem3,
            subject=self.sub_dbms,
            teacher=self.teacher_1,
            room=self.room_c301,
            time_slot=self.slot_mon_p1,
            class_type=TimetableEntry.ClassType.LECTURE
        )
        with self.assertRaises(ValidationError) as ctx:
            entry_invalid.save()

        self.assertIn("specify either a Section or a MergeGroup", str(ctx.exception))
