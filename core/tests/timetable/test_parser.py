from django.test import SimpleTestCase
from core.services.timetable.parser import parse_timetable_cell


class ParserTestCase(SimpleTestCase):
    def test_valid_lecture(self):
        """1. Valid lecture parsing: BCSE-634 Dr. Abhishek Bhattacherjee, 357"""
        cell = "BCSE-634 Dr. Abhishek Bhattacherjee, 357"
        parsed = parse_timetable_cell(cell)
        self.assertEqual(parsed.subject_code, "BCSE-634")
        self.assertEqual(parsed.teacher, "Dr. Abhishek Bhattacherjee")
        self.assertEqual(parsed.room, "357")
        self.assertEqual(parsed.class_type, "LECTURE")
        self.assertFalse(parsed.is_break)

    def test_valid_laboratory(self):
        """2. Valid laboratory parsing: BCSE-503L Ms. Neelam Oberoi, 160"""
        cell = "BCSE-503L Ms. Neelam Oberoi, 160"
        parsed = parse_timetable_cell(cell)
        self.assertEqual(parsed.subject_code, "BCSE-503L")
        self.assertEqual(parsed.teacher, "Ms. Neelam Oberoi")
        self.assertEqual(parsed.room, "160")
        self.assertEqual(parsed.class_type, "LAB")

    def test_teacher_names_with_punctuation(self):
        """3. Teacher names containing punctuation & titles."""
        test_cases = [
            ("BCSE-501 Dr. D.D Sharma, 119", "BCSE-501", "Dr. D.D Sharma", "119"),
            ("BCSE-502 Dr. Kajal Jain (D1), 260A", "BCSE-502", "Dr. Kajal Jain", "260A"),
            ("BCSE-503 Mr. Ankur Mangla (L), 165 T", "BCSE-503", "Mr. Ankur Mangla", "165 T"),
            ("BCSE-504 Dr.Puneet Banga, 145", "BCSE-504", "Dr.Puneet Banga", "145"),
        ]
        for cell, exp_sub, exp_teacher, exp_room in test_cases:
            parsed = parse_timetable_cell(cell)
            self.assertEqual(parsed.subject_code, exp_sub)
            self.assertEqual(parsed.teacher, exp_teacher)
            self.assertEqual(parsed.room, exp_room)

    def test_room_without_comma(self):
        """4. Room without comma: BCSE-501 Abhishek Pandey 119"""
        cell = "BCSE-501 Abhishek Pandey 119"
        parsed = parse_timetable_cell(cell)
        self.assertEqual(parsed.subject_code, "BCSE-501")
        self.assertEqual(parsed.teacher, "Abhishek Pandey")
        self.assertEqual(parsed.room, "119")

    def test_special_class(self):
        """5. Special class: PR-I Dr. Sonali Goyal, 357"""
        cell = "PR-I Dr. Sonali Goyal, 357"
        parsed = parse_timetable_cell(cell)
        self.assertEqual(parsed.subject_code, "PR-I")
        self.assertEqual(parsed.teacher, "Dr. Sonali Goyal")
        self.assertEqual(parsed.room, "357")
        self.assertEqual(parsed.class_type, "SPECIAL")

    def test_merge_group_notation(self):
        """14. (F,H,J merge) parsing."""
        cell = "BCSE-571 Dr. Mohit Chabbra (F,H,J merge), 269"
        parsed = parse_timetable_cell(cell)
        self.assertEqual(parsed.subject_code, "BCSE-571")
        self.assertEqual(parsed.teacher, "Dr. Mohit Chabbra")
        self.assertEqual(parsed.room, "269")
        self.assertEqual(parsed.merge_group, ["F", "H", "J"])

    def test_free_period(self):
        """16. Free period."""
        for val in ["FREE", "Free Period", "FREE PERIOD"]:
            parsed = parse_timetable_cell(val)
            self.assertTrue(parsed.is_break)
            self.assertEqual(parsed.class_type, "FREE")

    def test_lunch_and_break(self):
        """17 & 18. Lunch & Break."""
        parsed_lunch = parse_timetable_cell("Lunch Break")
        self.assertTrue(parsed_lunch.is_break)
        self.assertEqual(parsed_lunch.class_type, "LUNCH")

        parsed_break = parse_timetable_cell("BREAK")
        self.assertTrue(parsed_break.is_break)
        self.assertEqual(parsed_break.class_type, "BREAK")
