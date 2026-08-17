from django.test import TestCase
from core.services.timetable.parser import parse_timetable_cell, ParsedEntry


class TimetableParserTestCase(TestCase):
    def test_1_valid_lecture(self):
        """Test standard lecture parsing."""
        raw = "BCSE-634 Dr. Abhishek Bhattacherjee, 357"
        res = parse_timetable_cell(raw)
        self.assertEqual(res.subject_code, "BCSE-634")
        self.assertEqual(res.teacher, "Dr. Abhishek Bhattacherjee")
        self.assertEqual(res.room, "357")
        self.assertEqual(res.class_type, "LECTURE")
        self.assertFalse(res.is_break)
        self.assertFalse(res.is_formula)

    def test_2_valid_laboratory(self):
        """Test laboratory subject code detection."""
        raw = "BCSE-503L Ms. Neelam Oberoi, 160"
        res = parse_timetable_cell(raw)
        self.assertEqual(res.subject_code, "BCSE-503L")
        self.assertEqual(res.teacher, "Ms. Neelam Oberoi")
        self.assertEqual(res.room, "160")
        self.assertEqual(res.class_type, "LAB")

    def test_3_teacher_names_with_punctuation(self):
        """Test teacher names with dots, brackets, honorifics, and no spaces."""
        cases = [
            ("BCSE-601 Dr. D.D Sharma, 357", "Dr. D.D Sharma"),
            ("BCSE-502 Dr. Kajal Jain (D1), 357", "Dr. Kajal Jain"),
            ("BCSE-503 Mr. Ankur Mangla (L), 357", "Mr. Ankur Mangla"),
            ("BCSE-504 Dr.Puneet Banga, 357", "Dr.Puneet Banga"),
        ]
        for raw, expected_teacher in cases:
            res = parse_timetable_cell(raw)
            self.assertEqual(res.teacher, expected_teacher, f"Failed for {raw}")

    def test_4_room_without_comma(self):
        """Test room number extraction when separated by space without comma."""
        raw = "BCSE-501 Abhishek Pandey 119"
        res = parse_timetable_cell(raw)
        self.assertEqual(res.subject_code, "BCSE-501")
        self.assertEqual(res.teacher, "Abhishek Pandey")
        self.assertEqual(res.room, "119")

    def test_5_special_class(self):
        """Test special departmental activity entry."""
        raw = "PR-I Dr. Sonali Goyal, 357"
        res = parse_timetable_cell(raw)
        self.assertEqual(res.subject_code, "PR-I")
        self.assertEqual(res.teacher, "Dr. Sonali Goyal")
        self.assertEqual(res.room, "357")
        self.assertEqual(res.class_type, "SPECIAL")

    def test_14_merge_notation_parsing(self):
        """Test (F,H,J merge) and variations extraction."""
        cases = [
            ("BCSE-561 Dr. Sanjeev Rana (F, H, J merge), 269", ["F", "H", "J"]),
            ("BECE-550 Dr. Amit Jain (I, J Merge) 267", ["I", "J"]),
            ("BCSE- 542 Dr. Rohini (A,B Merge) , 208", ["A", "B"]),
            ("BCSE-533L Nikhil Patil ( D,E & L Merge), CSED", ["D", "E", "L"]),
        ]
        for raw, expected_groups in cases:
            res = parse_timetable_cell(raw)
            self.assertEqual(res.merge_group, expected_groups, f"Failed for {raw}")

    def test_16_free_period(self):
        """Test FREE period cells."""
        for val in ["FREE", "Free Period", "OFF", None, ""]:
            res = parse_timetable_cell(val)
            self.assertTrue(res.is_break)
            self.assertEqual(res.class_type, "FREE")

    def test_17_lunch(self):
        """Test Lunch cells."""
        for val in ["Lunch", "Lunch Break"]:
            res = parse_timetable_cell(val)
            self.assertTrue(res.is_break)
            self.assertEqual(res.class_type, "LUNCH")

    def test_18_break(self):
        """Test Break cells."""
        res = parse_timetable_cell("Short Break")
        self.assertTrue(res.is_break)
        self.assertEqual(res.class_type, "BREAK")

    def test_19_formula_cell(self):
        """Test formula cell detection."""
        raw = "=SUM(A1:B10)"
        res = parse_timetable_cell(raw)
        self.assertTrue(res.is_formula)
