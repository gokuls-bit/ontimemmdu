import io
import zipfile
from django.test import TestCase
from core.services.timetable.result import ImportResult
from core.services.timetable.security import validate_excel_security, MAX_FILE_SIZE


class TimetableSecurityTestCase(TestCase):
    def test_20_external_link_workbook(self):
        """Reject workbooks containing external links/references."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('xl/workbook.xml', '<workbook><externalReferences><externalReference r:id="rId1"/></externalReferences></workbook>')
            zf.writestr('[Content_Types].xml', '<Types></Types>')

        buf.name = "test_external.xlsx"
        result = ImportResult(file_name=buf.name)
        is_safe = validate_excel_security(buf, result)

        self.assertFalse(is_safe)
        self.assertTrue(any(e['error_code'] == 'EXTERNAL_LINK' for e in result.errors))

    def test_21_macro_enabled_workbook(self):
        """Reject macro-enabled workbooks (.xlsm / vbaProject.bin)."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('xl/vbaProject.bin', b'VBA BINARY DATA')

        buf.name = "test_macro.xlsm"
        result = ImportResult(file_name=buf.name)
        is_safe = validate_excel_security(buf, result)

        self.assertFalse(is_safe)
        self.assertTrue(any(e['error_code'] == 'MACRO_ENABLED' for e in result.errors))

    def test_22_oversized_file(self):
        """Reject files exceeding 10MB limit."""
        buf = io.BytesIO(b"A" * (MAX_FILE_SIZE + 1024))
        buf.name = "large_file.xlsx"
        result = ImportResult(file_name=buf.name)
        is_safe = validate_excel_security(buf, result)

        self.assertFalse(is_safe)
        self.assertTrue(any(e['error_code'] == 'FILE_TOO_LARGE' for e in result.errors))

    def test_23_disguised_non_xlsx_file(self):
        """Reject non-XLSX file disguised with .xlsx extension."""
        buf = io.BytesIO(b"NOT A ZIP FILE HEADER")
        buf.name = "fake.xlsx"
        result = ImportResult(file_name=buf.name)
        is_safe = validate_excel_security(buf, result)

        self.assertFalse(is_safe)
        self.assertTrue(any(e['error_code'] == 'CORRUPTED_WORKBOOK' for e in result.errors))

    def test_24_corrupted_xlsx(self):
        """Reject corrupted zip archive."""
        buf = io.BytesIO(b"PK\x03\x04CORRUPTED_ZIP_CONTENT_PAYLOAD")
        buf.name = "corrupt.xlsx"
        result = ImportResult(file_name=buf.name)
        is_safe = validate_excel_security(buf, result)

        self.assertFalse(is_safe)
        self.assertTrue(any(e['error_code'] == 'CORRUPTED_WORKBOOK' for e in result.errors))
