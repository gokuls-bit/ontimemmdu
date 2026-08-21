from django.test import TestCase
from timetable.models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from core.services.timetable.group_resolver import (
    validate_student_context, resolve_group_entry
)
from core.services.timetable.exceptions import (
    InvalidStudentContext, InvalidSemester, InvalidSection, InvalidGroup
)


class GroupResolverTestCase(TestCase):
    def setUp(self):
        self.sem5 = Semester.objects.create(number=5, academic_year="2026-27")
        self.sec_a = Section.objects.create(name="5CSEA1", semester=self.sem5, capacity=60)
        self.sec_b = Section.objects.create(name="5CSEB1", semester=self.sem5, capacity=60)

        self.grp_g1 = Group.objects.create(name="G1", section=self.sec_a)
        self.grp_g2 = Group.objects.create(name="G2", section=self.sec_a)

        self.grp_f = Group.objects.create(name="F", section=self.sec_a)
        self.grp_h = Group.objects.create(name="H", section=self.sec_a)
        self.grp_j = Group.objects.create(name="J", section=self.sec_b)

        self.merge_fhj = MergeGroup.objects.create(name="5Sem-F_H_J")
        self.merge_fhj.groups.add(self.grp_f, self.grp_h, self.grp_j)

        self.sub_dbms = Subject.objects.create(code="BCSE-501", name="DBMS", short_name="DBMS", semester=self.sem5)
        self.sub_lab = Subject.objects.create(code="BCSE-501L", name="DBMS Lab", short_name="DBMS Lab", semester=self.sem5)

        self.teacher = Teacher.objects.create(employee_id="T001", first_name="Alan", last_name="Turing", email="alan@cse.edu")
        self.room_c301 = Room.objects.create(room_number="C-301", capacity=70)
        self.room_lab2 = Room.objects.create(room_number="Lab-2", capacity=35)

        self.slot_p1 = TimeSlot.objects.create(day="MON", period=1, start_time="08:40", end_time="09:40")
        self.slot_p2 = TimeSlot.objects.create(day="MON", period=2, start_time="09:40", end_time="10:40")

    def test_valid_student_context_resolution(self):
        """Valid student context resolution."""
        sem, sec, grp = validate_student_context(5, "5CSEA1", "G1")
        self.assertEqual(sem, self.sem5)
        self.assertEqual(sec, self.sec_a)
        self.assertEqual(grp, self.grp_g1)

    def test_invalid_semester_raises_error(self):
        """19. Invalid semester error."""
        with self.assertRaises(InvalidSemester):
            validate_student_context(9, "5CSEA1", "G1")

    def test_invalid_section_raises_error(self):
        """20. Invalid section error."""
        with self.assertRaises(InvalidSection):
            validate_student_context(5, "INVALID_SEC", "G1")

    def test_invalid_group_raises_error(self):
        """21. Invalid group error (Section A + Group 3)."""
        with self.assertRaises(InvalidGroup):
            validate_student_context(5, "5CSEA1", "G3")

    def test_section_without_groups(self):
        """22. Section without groups (group is None)."""
        sem, sec, grp = validate_student_context(5, "5CSEA1", None)
        self.assertEqual(sem, self.sem5)
        self.assertEqual(sec, self.sec_a)
        self.assertIsNone(grp)

    def test_direct_group_assignment(self):
        """23. Direct group assignment resolution."""
        tt = TimetableEntry.objects.create(
            semester=self.sem5, section=self.sec_a, group=self.grp_g1,
            subject=self.sub_dbms, teacher=self.teacher, room=self.room_c301,
            time_slot=self.slot_p1
        )
        entry, override, cancelled = resolve_group_entry(self.sem5, self.sec_a, self.grp_g1, "MON", 1)
        self.assertEqual(entry, tt)
        self.assertFalse(cancelled)

    def test_merged_group_assignment(self):
        """24 & 25. Shared/Merged group assignment (F,H,J merge)."""
        tt_merge = TimetableEntry.objects.create(
            semester=self.sem5, merge_group=self.merge_fhj,
            subject=self.sub_lab, teacher=self.teacher, room=self.room_lab2,
            time_slot=self.slot_p2
        )
        # Student in Group F
        entry_f, _, _ = resolve_group_entry(self.sem5, self.sec_a, self.grp_f, "MON", 2)
        # Student in Group J (Section B)
        entry_j, _, _ = resolve_group_entry(self.sem5, self.sec_b, self.grp_j, "MON", 2)

        self.assertEqual(entry_f, tt_merge)
        self.assertEqual(entry_j, tt_merge)
        self.assertEqual(entry_f.room, entry_j.room)
