import json
import os
import datetime
from typing import Any, List, Dict
from django.db import transaction
from .result import ImportResult
from .parser import parse_timetable_cell, ParsedEntry
from .validator import validate_parsed_entries, normalize_day
from .security import sanitize_text
from timetable.models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)


def import_timetable_json(file_input: Any, academic_year: str = "2026-27") -> ImportResult:
    """
    Imports timetable JSON datasets (such as cse_smartroom_3rd_5th_semester_complete.json
    or cse_smartroom_timetable_data.json) into the Django/PostgreSQL database.
    
    Maps JSON entries into the exact same ParsedEntry -> Validator -> PostgreSQL pipeline.
    """
    filename = getattr(file_input, 'name', str(file_input))
    result = ImportResult(file_name=filename)

    # 1. Read JSON file content
    data = None
    try:
        if isinstance(file_input, str):
            with open(file_input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            content = file_input.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            data = json.loads(content)
    except Exception as e:
        result.add_error("CORRUPTED_WORKBOOK", f"Failed to parse JSON file: {str(e)}")
        return result

    parsed_entries: List[ParsedEntry] = []
    discovered_sections: set = set()
    discovered_semesters: set = set()

    # Handle single sheet vs multi-semester dataset structures
    raw_entries = []
    if isinstance(data, dict):
        if "timetable_entries" in data:
            raw_entries = data["timetable_entries"]
        elif "entries" in data:
            raw_entries = data["entries"]

        if "semesters" in data:
            for sem in data.get("semesters", []):
                sem_title = sem.get("semester")
                if sem_title:
                    discovered_semesters.add(sem_title)

        if "sections" in data:
            for s in data["sections"]:
                if isinstance(s, dict) and "section_code" in s:
                    discovered_sections.add(s["section_code"])
                elif isinstance(s, str):
                    discovered_sections.add(s)

    elif isinstance(data, list):
        raw_entries = data

    # 2. Extract ParsedEntry objects from raw JSON records
    for item in raw_entries:
        if not isinstance(item, dict):
            continue

        raw_str = item.get("raw") or ""
        sec_code = item.get("section") or ""
        day_raw = item.get("day") or ""
        period_num = item.get("period") or 1
        source_info = item.get("source") or {}

        sheet_name = source_info.get("sheet") if isinstance(source_info, dict) else ""
        cell_coord = source_info.get("cell") if isinstance(source_info, dict) else ""

        ctx = {
            'sheet': sheet_name,
            'cell': cell_coord,
            'section': sec_code,
            'day': day_raw,
            'period': period_num
        }

        # Use parse_timetable_cell on raw text if available
        if raw_str:
            parsed = parse_timetable_cell(raw_str, context=ctx)
        else:
            # Fallback construct from JSON fields
            parsed = ParsedEntry(
                raw=f"{item.get('subject_code', '')} {item.get('teacher', '')} {item.get('room', '')}",
                class_type=item.get("entry_type") or item.get("class_type") or "LECTURE",
                subject_code=item.get("subject_code") or item.get("subject"),
                subject_name=item.get("subject_name"),
                teacher=item.get("teacher"),
                room=item.get("room"),
                merge_group=item.get("merge_group") if isinstance(item.get("merge_group"), list) else None,
                notes=item.get("notes"),
                context=ctx
            )

        if sec_code:
            discovered_sections.add(sec_code)

        parsed_entries.append(parsed)

    result.parsed_count = len(parsed_entries)
    result.sections_count = len(discovered_sections)
    result.semester = "3rd & 5th Semester Dataset" if len(discovered_semesters) > 1 else (list(discovered_semesters)[0] if discovered_semesters else "3rd Semester")

    # 3. Validate Parsed Entries
    is_valid = validate_parsed_entries(parsed_entries, result)
    if not is_valid or result.error_count > 0:
        return result

    # 4. Atomic Database Transaction
    try:
        with transaction.atomic():
            sem_obj, _ = Semester.objects.get_or_create(
                number=3,
                academic_year=academic_year,
                defaults={'is_active': True}
            )

            # Slot Map
            slot_map: Dict[Tuple[str, int], TimeSlot] = {}
            for d_code in ['MON', 'TUE', 'WED', 'THU', 'FRI']:
                for p in range(1, 9):
                    s_hr = 8 + p if p <= 4 else 9 + p
                    ts, _ = TimeSlot.objects.get_or_create(
                        day=d_code,
                        period=p,
                        defaults={
                            'start_time': datetime.time(s_hr, 0),
                            'end_time': datetime.time(s_hr + 1, 0)
                        }
                    )
                    slot_map[(d_code, p)] = ts

            section_objs: Dict[str, Section] = {}
            for sec_name in discovered_sections:
                sec_obj, _ = Section.objects.get_or_create(
                    name=sec_name,
                    semester=sem_obj,
                    defaults={'capacity': 60}
                )
                section_objs[sec_name] = sec_obj

            merge_group_objs: Dict[str, MergeGroup] = {}
            entries_to_create = []

            for entry in parsed_entries:
                if entry.is_break:
                    continue

                ctx = entry.context
                sec_name = ctx.get('section')
                day_code = normalize_day(ctx.get('day'))
                period_num = ctx.get('period')

                sec_obj = section_objs.get(sec_name)
                ts_obj = slot_map.get((day_code, period_num)) or TimeSlot.objects.filter(day=day_code, period=period_num).first()

                if not ts_obj:
                    ts_obj = TimeSlot.objects.create(
                        day=day_code,
                        period=period_num,
                        start_time=datetime.time(9, 0),
                        end_time=datetime.time(10, 0)
                    )

                sub_code = entry.subject_code or "SPEC-00"
                sub_obj, _ = Subject.objects.get_or_create(
                    code=sub_code,
                    defaults={
                        'name': entry.subject_name or sub_code,
                        'short_name': sub_code,
                        'subject_type': entry.class_type if entry.class_type in Subject.SubjectType.values else Subject.SubjectType.THEORY,
                        'semester': sem_obj
                    }
                )

                t_name = entry.teacher or "Faculty Staff"
                fname = t_name.split()[0] if t_name else "Faculty"
                lname = " ".join(t_name.split()[1:]) if len(t_name.split()) > 1 else "Staff"
                emp_id = f"EMP-{hash(t_name) % 100000:05d}"

                teacher_obj = Teacher.objects.filter(first_name=fname, last_name=lname).first()
                if not teacher_obj:
                    teacher_obj, _ = Teacher.objects.get_or_create(
                        employee_id=emp_id,
                        defaults={
                            'first_name': fname,
                            'last_name': lname,
                            'email': f"{fname.lower()}.{lname.lower().replace(' ', '')}@cse.edu",
                            'designation': 'Assistant Professor'
                        }
                    )

                r_num = entry.room or "C-301"
                room_obj, _ = Room.objects.get_or_create(
                    room_number=r_num,
                    defaults={
                        'building': 'Engineering Block C',
                        'room_type': Room.RoomType.LAB if entry.class_type == 'LAB' else Room.RoomType.LECTURE_HALL,
                        'capacity': 35 if entry.class_type == 'LAB' else 70
                    }
                )

                merge_group_obj = None
                if entry.merge_group:
                    mg_name_str = "_".join(sorted(entry.merge_group))
                    mg_key = f"{sem_obj.number}Sem-{mg_name_str}"
                    if mg_key not in merge_group_objs:
                        mg_obj, _ = MergeGroup.objects.get_or_create(
                            name=mg_key,
                            defaults={'description': f"Merged group for sections/groups: {', '.join(entry.merge_group)}"}
                        )
                        merge_group_objs[mg_key] = mg_obj

                        if sec_obj:
                            for grp_letter in entry.merge_group:
                                grp_obj, _ = Group.objects.get_or_create(name=grp_letter, section=sec_obj)
                                mg_obj.groups.add(grp_obj)

                    merge_group_obj = merge_group_objs[mg_key]
                    result.merge_groups_count = len(merge_group_objs)

                tt_entry = TimetableEntry(
                    semester=sem_obj,
                    section=sec_obj if not merge_group_obj else sec_obj,
                    merge_group=merge_group_obj,
                    subject=sub_obj,
                    teacher=teacher_obj,
                    room=room_obj,
                    time_slot=ts_obj,
                    day=day_code,
                    period=period_num,
                    start_time=ts_obj.start_time,
                    end_time=ts_obj.end_time,
                    class_type=TimetableEntry.ClassType.LAB if entry.class_type == 'LAB' else TimetableEntry.ClassType.LECTURE
                )
                entries_to_create.append(tt_entry)

            for tt in entries_to_create:
                tt.save()

            result.imported_count = len(entries_to_create)
            result.success = True

    except Exception as e:
        result.add_error("TRANSACTION_FAILED", f"JSON database import failed: {str(e)}")
        result.success = False

    return result
