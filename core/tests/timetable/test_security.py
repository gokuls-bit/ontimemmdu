import io
import zipfile
from django.test import SimpleTestCase
from core.services.timetable.result import ImportResult
from core.services.timetable.security import validate_excel_security, sanitize_text
from core.services.timetable.downloads import get_whitelisted_file_path


class SecurityTestCase(SimpleTestCase):
    def test_sanitize_text(self):
        """Verify string sanitization removes control characters and normalizes spaces."""
        raw = "  Dr.\x00 Abhishek \t\n Bhattacherjee  \x1f "
        sanitized = sanitize_text(raw)
        self.assertEqual(sanitized, "Dr. Abhishek Bhattacherjee")

    def test_disguised_non_xlsx_file(self):
        """23. Disguised non-XLSX file rejection."""
        result = ImportResult()
        fake_file = io.BytesIO(b"Not a zip file content")
        fake_file.name = "fake.xlsx"
        res = validate_excel_security(fake_file, result)
        self.assertFalse(res)
        self.assertEqual(result.errors[0]['error_code'], "CORRUPTED_WORKBOOK")

    def test_macro_enabled_workbook_rejection(self):
        """21. Macro-enabled workbook rejection."""
        result = ImportResult()
        fake_file = io.BytesIO(b"PK\x03\x04fake_xlsm_content")
        fake_file.name = "malicious.xlsm"
        res = validate_excel_security(fake_file, result)
        self.assertFalse(res)
        self.assertEqual(result.errors[0]['error_code'], "MACRO_ENABLED")

    def test_zip_with_vba_macro_rejection(self):
        """21. Macro stream inside zip file rejection."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('xl/vbaProject.bin', b'macro binary')
            zf.writestr('xl/workbook.xml', b'<workbook/>')

        buffer.seek(0)
        buffer.name = "macro_hidden.xlsx"
        result = ImportResult()
        res = validate_excel_security(buffer, result)
        self.assertFalse(res)
        self.assertEqual(result.errors[0]['error_code'], "MACRO_ENABLED")

    def test_external_link_workbook_rejection(self):
        """20. External-link workbook rejection."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('xl/externalLinks/externalLink1.xml', b'<externalLink/>')
            zf.writestr('xl/workbook.xml', b'<workbook/>')

        buffer.seek(0)
        buffer.name = "external_link.xlsx"
        result = ImportResult()
        res = validate_excel_security(buffer, result)
        self.assertFalse(res)
        self.assertEqual(result.errors[0]['error_code'], "EXTERNAL_LINK")

    def test_oversized_file_rejection(self):
        """22. Oversized file rejection (> 10MB)."""
        buffer = io.BytesIO(b"0" * (11 * 1024 * 1024))
        buffer.name = "huge.xlsx"
        result = ImportResult()
        res = validate_excel_security(buffer, result)
        self.assertFalse(res)
        self.assertEqual(result.errors[0]['error_code'], "FILE_TOO_LARGE")

    def test_path_traversal_attempt_against_download(self):
        """32 & 33. Path traversal and unregistered file download attempt."""
        path, content_type, err = get_whitelisted_file_path("../../etc/passwd", "json")
        self.assertIsNone(path)
        self.assertEqual(err, "UNREGISTERED_FILE")

        path_unreg, content_type_unreg, err_unreg = get_whitelisted_file_path("99th", "excel")
        self.assertIsNone(path_unreg)
        self.assertEqual(err_unreg, "UNREGISTERED_FILE")
