import os
import re
import zipfile
import io
from typing import Tuple, Optional, Any
from .result import ImportResult

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit


def sanitize_text(value: Any, max_length: int = 500) -> str:
    """
    Sanitizes string extracted from Excel or JSON:
    - Converts value to string
    - Removes control characters
    - Normalizes multiple spaces/newlines to single space
    - Strips leading and trailing whitespace
    - Enforces maximum string length
    """
    if value is None:
        return ""

    text = str(value)
    # Remove ASCII control characters (0-31, 127) except tab/newline if needed, but for timetable titles clean all
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text[:max_length]


def validate_excel_security(file_input: Any, result: ImportResult) -> bool:
    """
    Validates Excel file security before parsing:
    - Maximum file size check
    - File extension validation (.xlsx only)
    - XLSX ZIP magic signature validation (PK\\x03\\x04)
    - Macro detection (vbaProject.bin)
    - External links detection (externalReferences / xl/externalLinks/)
    """
    filename = ""
    file_bytes = b""

    if isinstance(file_input, str):
        filename = file_input
        if not os.path.exists(file_input):
            result.add_error("INVALID_FILE", f"File '{file_input}' does not exist.")
            return False

        file_size = os.path.getsize(file_input)
        if file_size > MAX_FILE_SIZE:
            result.add_error("FILE_TOO_LARGE", f"File size ({file_size} bytes) exceeds maximum limit of 10 MB.")
            return False

        with open(file_input, "rb") as f:
            file_bytes = f.read()
    else:
        # File-like object (UploadedFile or BytesIO)
        filename = getattr(file_input, 'name', 'uploaded_file.xlsx')
        file_input.seek(0, os.SEEK_END)
        file_size = file_input.tell()
        file_input.seek(0)

        if file_size > MAX_FILE_SIZE:
            result.add_error("FILE_TOO_LARGE", f"File size ({file_size} bytes) exceeds maximum limit of 10 MB.")
            return False

        file_bytes = file_input.read()
        file_input.seek(0)

    # 1. Extension Check
    lower_name = filename.lower()
    if lower_name.endswith(('.xlsm', '.xltm')):
        result.add_error("MACRO_ENABLED", "Macro-enabled Excel files (.xlsm, .xltm) are strictly prohibited.")
        return False
    elif lower_name.endswith('.xls'):
        result.add_error("INVALID_FILE", "Legacy Excel files (.xls) are not allowed. Please upload .xlsx files.")
        return False
    elif not lower_name.endswith('.xlsx'):
        result.add_error("INVALID_FILE", "Only standard .xlsx Excel workbooks are supported.")
        return False

    # 2. Magic Signature Validation (PK\x03\x04)
    if not file_bytes.startswith(b'PK\x03\x04'):
        result.add_error("CORRUPTED_WORKBOOK", "File signature is invalid or disguised. Expected a valid XLSX archive.")
        return False

    # 3. Zip Content Inspection (Macros & External Links)
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            namelist = zf.namelist()

            # Check for VBA Macros
            for name in namelist:
                if 'vbaProject.bin' in name or name.endswith('.bin'):
                    result.add_error("MACRO_ENABLED", "Workbook contains macros (vbaProject.bin), which are strictly prohibited.")
                    return False

            # Check for External Workbook Links
            for name in namelist:
                if 'externalLinks/' in name or 'externalReferences' in name:
                    result.add_error("EXTERNAL_LINK", "Workbook contains external links, which are strictly prohibited.")
                    return False

            # Check workbook.xml for external references tag
            if 'xl/workbook.xml' in namelist:
                workbook_xml = zf.read('xl/workbook.xml').decode('utf-8', errors='ignore')
                if '<externalReferences' in workbook_xml:
                    result.add_error("EXTERNAL_LINK", "Workbook contains external workbook references, which are strictly prohibited.")
                    return False

    except zipfile.BadZipFile:
        result.add_error("CORRUPTED_WORKBOOK", "Unable to unpack Excel file. File is corrupted or invalid ZIP format.")
        return False
    except Exception as e:
        result.add_error("CORRUPTED_WORKBOOK", f"Error inspecting Excel zip contents: {str(e)}")
        return False

    return True
