import os
from pathlib import Path
from typing import Dict, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
HELPCSE_DIR = BASE_DIR / "smartroom" / "helpcse"
FIXTURES_DIR = BASE_DIR / "fixtures"

# Server-side explicit whitelist mapping. NEVER construct paths from user input.
DOWNLOAD_WHITELIST: Dict[str, Path] = {
    "3rd_json": HELPCSE_DIR / "cse_smartroom_3rd_5th_semester_complete.json",
    "5th_json": HELPCSE_DIR / "cse_smartroom_3rd_5th_semester_complete.json",
    "4th_json": HELPCSE_DIR / "cse_smartroom_timetable_data.json",
    "sample_json": FIXTURES_DIR / "sample_timetable.json",
    "3rd_excel": HELPCSE_DIR / "3rd_CSE_Classwise_Time_Table.xlsx",
    "4th_excel": HELPCSE_DIR / "4th_CSE_Classwise_Time_Table.xlsx",
    "5th_excel": HELPCSE_DIR / "5th_CSE_Classwise_Time_Table.xlsx",
}


def get_whitelisted_file_path(semester_code: str, file_format: str) -> Tuple[Optional[Path], Optional[str]]:
    """
    Returns the trusted file Path and content type for a given semester_code and file_format.
    Strictly validates against DOWNLOAD_WHITELIST to prevent path traversal.
    """
    key = f"{semester_code.lower()}_{file_format.lower()}"
    file_path = DOWNLOAD_WHITELIST.get(key)

    if not file_path:
        return None, "UNREGISTERED_FILE"

    # Resolve realpath to ensure no symlink traversal escapes
    resolved = file_path.resolve()
    
    # Verify file exists
    if not resolved.exists():
        # For excel files if missing physically on disk, handle gracefully
        return None, "FILE_NOT_FOUND"

    content_type = "application/json" if file_format.lower() == "json" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return resolved, content_type
