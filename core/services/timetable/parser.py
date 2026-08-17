import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from .security import sanitize_text


@dataclass
class ParsedEntry:
    raw: str
    class_type: str = "LECTURE"  # LECTURE, LAB, TUTORIAL, SPECIAL, FREE, BREAK, LUNCH
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    teacher: Optional[str] = None
    room: Optional[str] = None
    merge_group: Optional[List[str]] = None
    notes: Optional[str] = None
    is_break: bool = False
    is_formula: bool = False
    context: Dict[str, Any] = field(default_factory=dict)


# Known subject code patterns
STD_SUBJECT_REGEX = re.compile(r'\b([A-Z]{2,5}-\d{3,4}[A-Z]?|[A-Z]{2,5}\d{3}[A-Z]?)\b', re.IGNORECASE)
SPECIAL_SUBJECT_REGEX = re.compile(r'\b(PR-[I|V|X\d]+|PR\d+|HVE|APTITUDE|TRAINING|SEMINAR|VALUE\s+ADDED)\b', re.IGNORECASE)

# Room patterns
ROOM_REGEX = re.compile(
    r'(?:,\s*|\s+)(Lab-\d+|[1-4]\d{2}[A-Z]?|[1-4]\d{2}\s?[A-Z]?|T-\d+|CSED|\d{3}\s?T|\(\d{3}\))\s*$',
    re.IGNORECASE
)

# Merge group notation patterns: (F,H,J merge), (B, K Merge), F,H,J merge
MERGE_REGEX = re.compile(
    r'\(([^)]*?\bmerge\b[^)]*?)\)|\(([^)]*?\bMerge\b[^)]*?)\)|([A-Z0-9,\s]+\bmerge\b)',
    re.IGNORECASE
)


def parse_timetable_cell(value: Any, context: Optional[Dict[str, Any]] = None) -> ParsedEntry:
    """
    Parses a single timetable cell string or cell object into a structured ParsedEntry.
    """
    ctx = context or {}
    if value is None:
        return ParsedEntry(raw="", class_type="FREE", is_break=True, context=ctx)

    raw_str = str(value).strip()

    # 1. Check Formula
    if raw_str.startswith('='):
        return ParsedEntry(
            raw=raw_str,
            is_formula=True,
            notes="Formula cell detected",
            context=ctx
        )

    sanitized = sanitize_text(raw_str)
    if not sanitized:
        return ParsedEntry(raw=raw_str, class_type="FREE", is_break=True, context=ctx)

    upper_val = sanitized.upper()

    # 2. Check Free / Break / Lunch
    if upper_val in {"FREE", "FREE PERIOD", "OFF", "NIL", "N/A"}:
        return ParsedEntry(raw=sanitized, class_type="FREE", is_break=True, context=ctx)
    if "BREAK" in upper_val and "LUNCH" not in upper_val:
        return ParsedEntry(raw=sanitized, class_type="BREAK", is_break=True, context=ctx)
    if "LUNCH" in upper_val:
        return ParsedEntry(raw=sanitized, class_type="LUNCH", is_break=True, context=ctx)

    entry = ParsedEntry(raw=sanitized, context=ctx)
    working_str = sanitized

    # 3. Extract Merge Group Notation e.g., (F,H,J merge) or (B, K Merge)
    merge_match = MERGE_REGEX.search(working_str)
    if merge_match:
        full_match = merge_match.group(0)
        # Extract individual section/group letters e.g., "F,H,J" -> ['F', 'H', 'J']
        content = merge_match.group(1) or merge_match.group(2) or merge_match.group(3) or ""
        clean_content = re.sub(r'\bmerge\b', '', content, flags=re.IGNORECASE)
        groups = [g.strip() for g in re.split(r'[,+\s]+', clean_content) if g.strip()]
        if groups:
            entry.merge_group = groups

        # Remove merge notation from working string
        working_str = working_str.replace(full_match, ' ').strip()
        working_str = re.sub(r'\s+', ' ', working_str)

    # 4. Extract Room Number (at the end of string or after comma)
    room_match = ROOM_REGEX.search(working_str)
    if room_match:
        room_str = room_match.group(1).strip().strip('()')
        entry.room = sanitize_text(room_str)
        working_str = working_str[:room_match.start()].strip()
    else:
        # Secondary fallback room match: trailing 3-digit number or 260A style if preceded by comma or space
        fallback_room = re.search(r'(?:,\s*|\s+)([1-4]\d{2}[A-Z]?|Lab-\d+)$', working_str, re.IGNORECASE)
        if fallback_room:
            entry.room = sanitize_text(fallback_room.group(1))
            working_str = working_str[:fallback_room.start()].strip()

    # Clean trailing/leading commas from working_str
    working_str = working_str.strip(', ').strip()

    # 5. Extract Subject Code
    sub_match = STD_SUBJECT_REGEX.search(working_str)
    if sub_match:
        entry.subject_code = sub_match.group(1).upper()
        # Remove subject code from working_str to isolate teacher name
        working_str = working_str[:sub_match.start()] + ' ' + working_str[sub_match.end():]
        working_str = re.sub(r'\s+', ' ', working_str).strip()

        # Classify LAB if code ends in L e.g. BCSE-503L
        if entry.subject_code.endswith('L') or 'LAB' in sanitized.upper():
            entry.class_type = "LAB"
    else:
        # Check special subject code e.g. PR-I, HVE
        special_match = SPECIAL_SUBJECT_REGEX.search(working_str)
        if special_match:
            entry.subject_code = special_match.group(1).upper()
            entry.class_type = "SPECIAL"
            working_str = working_str[:special_match.start()] + ' ' + working_str[special_match.end():]
            working_str = re.sub(r'\s+', ' ', working_str).strip()

    # 6. Extract Teacher Name
    # Clean working_str
    working_str = re.sub(r'^[,\s\-]+|[,\s\-]+$', '', working_str)

    if working_str:
        # Remove unwanted trailing notes like "(1)", "(L)", "(D1)" if they were attached
        clean_teacher = re.sub(r'\s*\([A-Z0-9]+\)\s*$', '', working_str, flags=re.IGNORECASE).strip()
        clean_teacher = re.sub(r'^(\d+[A-Z]?,?\s*)', '', clean_teacher).strip()  # remove leading section prefix e.g. "3A,"
        if clean_teacher:
            entry.teacher = sanitize_text(clean_teacher)

    # If subject was marked special or lab, preserve class_type
    if not entry.class_type:
        entry.class_type = "LECTURE"

    return entry
