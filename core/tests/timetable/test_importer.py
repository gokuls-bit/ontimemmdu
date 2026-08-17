import io
import json
import openpyxl
from django.test import TestCase
from timetable.models import Semester, Section, TimetableEntry, Room, Teacher, Subject, MergeGroup
from core.services.timetable.importer import import_timetable
from core.services.timetable.json_importer import import_timetable_json
from core.services.timetable.parser import ParsedEntry
from core.services.timetable.validator import validate_parsed_entries
from core.services.timetable.result import ImportResult


def create_mock_workbook_bytes(sheet_name="3rd Semester", rows=None, merged_ranges=None):
    """Creates a temporary in-memory openpyxl workbook as BytesIO."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Header rows
    ws.cell(row=1, column=1, value="CSE DEPARTMENT TIMETABLE")
    ws.cell(row=2, column=1, value="DAY")
    ws.cell(row=2, column=2, value="SECTION")
    for p in range(1, 9):
        ws.cell(row=2, column=p + 2, value=str(p))

    # Add data rows
    if rows:
        for r_idx, row_data in enumerate(rows, start=3):
            ws.cell(row=r_idx, column=1, value=row_data[0])  # Day
            ws.cell(row=r_idx, column=2, value=row_data[1])  # Section
            for p_idx, cell_val in enumerate(row_data[2:], start=3):
                ws.cell(row=r_idx, column=p_idx, value=cell_val)

    if merged_ranges:
        for m_range in merged_ranges:
            ws.merge_cells(m_range)

    buf = io.BytesIO()
    wb.save(buf)
    buf.name = f"{sheet_name}_Classwise_Time_Table.xlsx"
    buf.seek(0)
    return buf


class TimetableImporterTestCase(TestCase):
    def test_6_missing_subject(self):
        """Reject entry with teacher and room but no valid subject."""
        entry = ParsedEntry(raw="Dr. Abhishek, 357", teacher="Dr. Abhishek", room="357", context={'section': '3CSEA1', 'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry], res)
        self.assertFalse(valid)
        self.assertTrue(any(e['error_code'] == 'MISSING_SUBJECT' for e in res.errors))

    def test_7_missing_teacher(self):
        """Reject entry with subject and room but no teacher."""
        entry = ParsedEntry(raw="BCSE-634 357", subject_code="BCSE-634", room="357", context={'section': '3CSEA1', 'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry], res)
        self.assertFalse(valid)
        self.assertTrue(any(e['error_code'] == 'MISSING_TEACHER' for e in res.errors))

    def test_8_missing_room(self):
        """Reject entry with subject and teacher but missing room."""
        entry = ParsedEntry(raw="BCSE-634 Dr. Abhishek", subject_code="BCSE-634", teacher="Dr. Abhishek", context={'section': '3CSEA1', 'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry], res)
        self.assertFalse(valid)
        self.assertTrue(any(e['error_code'] == 'MISSING_ROOM' for e in res.errors))

    def test_10_invalid_section(self):
        """Reject entry missing section context."""
        entry = ParsedEntry(raw="BCSE-634 Dr. Abhishek, 357", subject_code="BCSE-634", teacher="Dr. Abhishek", room="357", context={'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry], res)
        self.assertFalse(valid)
        self.assertTrue(any(e['error_code'] == 'INVALID_SECTION' for e in res.errors))

    def test_12_duplicate_room_booking(self):
        """Detect room double booking across independent sections."""
        entry1 = ParsedEntry(raw="BCSE-634 Dr. Alan, 357", subject_code="BCSE-634", teacher="Dr. Alan", room="357", context={'section': '3CSEA1', 'day': 'MON', 'period': 1})
        entry2 = ParsedEntry(raw="BCSE-501 Dr. Ada, 357", subject_code="BCSE-501", teacher="Dr. Ada", room="357", context={'section': '3CSEB1', 'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry1, entry2], res)
        self.assertFalse(valid)
        self.assertTrue(any(e['error_code'] == 'DUPLICATE_ROOM_BOOKING' for e in res.errors))

    def test_13_legitimate_shared_room(self):
        """Allow shared room when timetable cells contain merge notation."""
        entry1 = ParsedEntry(raw="BCSE-561 Dr. Rana (F,H merge), 269", subject_code="BCSE-561", teacher="Dr. Rana", room="269", merge_group=['F', 'H'], context={'section': '3CSEA1', 'day': 'MON', 'period': 1})
        entry2 = ParsedEntry(raw="BCSE-561 Dr. Rana (F,H merge), 269", subject_code="BCSE-561", teacher="Dr. Rana", room="269", merge_group=['F', 'H'], context={'section': '3CSEB1', 'day': 'MON', 'period': 1})
        res = ImportResult()
        valid = validate_parsed_entries([entry1, entry2], res)
        self.assertTrue(valid)

    def test_15_excel_worksheet_merged_cells(self):
        """Verify openpyxl load preserves merged_cells ranges."""
        buf = create_mock_workbook_bytes(sheet_name="3rd Semester", rows=[["MON", "3CSEA1", "BCSE-634 Dr. Abhishek, 357", "FREE"]], merged_ranges=["C3:D3"])
        wb = openpyxl.load_workbook(buf, data_only=True)
        ws = wb.active
        self.assertTrue(len(ws.merged_cells.ranges) > 0)

    def test_25_transaction_rollback(self):
        """Ensure full transaction rollback when validation fails."""
        initial_count = TimetableEntry.objects.count()
        buf = create_mock_workbook_bytes(
            sheet_name="3rd Semester",
            rows=[
                ["MON", "3CSEA1", "BCSE-634 Dr. Abhishek, 357", "FREE"],
                ["MON", "3CSEB1", "BCSE-501 Dr. MissingRoom", "FREE"]  # Error row: missing room
            ]
        )
        res = import_timetable(buf)
        self.assertFalse(res.success)
        self.assertEqual(TimetableEntry.objects.count(), initial_count)

    def test_26_valid_3rd_semester_workbook(self):
        """Import valid 3rd semester mock workbook into PostgreSQL."""
        buf = create_mock_workbook_bytes(
            sheet_name="3rd Semester",
            rows=[["MON", "3CSEA1", "BCSE-301 Dr. Abhishek, 357", "BCSE-302 Dr. Kajal, 358"]]
        )
        res = import_timetable(buf)
        self.assertTrue(res.success)
        self.assertEqual(res.imported_count, 2)
        self.assertTrue(Semester.objects.filter(number=3).exists())

    def test_27_valid_4th_semester_workbook(self):
        """Import valid 4th semester mock workbook into PostgreSQL."""
        buf = create_mock_workbook_bytes(
            sheet_name="4th Semester",
            rows=[["MON", "4CSEA1", "BCSE-401 Mr. Ankur, 250", "BCSE-402 Ms. Neelam, 251"]]
        )
        res = import_timetable(buf)
        self.assertTrue(res.success)
        self.assertEqual(res.imported_count, 2)
        self.assertTrue(Semester.objects.filter(number=4).exists())

    def test_28_valid_5th_semester_workbook(self):
        """Import valid 5th semester mock workbook into PostgreSQL."""
        buf = create_mock_workbook_bytes(
            sheet_name="5th Semester",
            rows=[["MON", "5CSEA1", "BCSE-501 Dr. Puneet, 160", "BCSE-502L Ms. Oberoi, 161"]]
        )
        res = import_timetable(buf)
        self.assertTrue(res.success)
        self.assertEqual(res.imported_count, 2)
        self.assertTrue(Semester.objects.filter(number=5).exists())

    def test_29_json_import(self):
        """Import timetable JSON dataset into PostgreSQL."""
        dataset = {
            "semesters": [{"semester": "3rd Semester"}],
            "sections": ["3CSEA1"],
            "timetable_entries": [
                {
                    "day": "Monday",
                    "period": 1,
                    "section": "3CSEA1",
                    "raw": "BCSE-301 Dr. Abhishek, 357",
                    "subject_code": "BCSE-301",
                    "teacher": "Dr. Abhishek",
                    "room": "357",
                    "class_type": "LECTURE"
                }
            ]
        }
        buf = io.BytesIO(json.dumps(dataset).encode('utf-8'))
        buf.name = "sample_test.json"
        res = import_timetable_json(buf)
        self.assertTrue(res.success)
        self.assertEqual(res.imported_count, 1)
