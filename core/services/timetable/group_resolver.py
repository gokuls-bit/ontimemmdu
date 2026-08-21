import datetime
from typing import Optional, Tuple, Any, List
from django.db.models import Q
from timetable.models import (
    Semester, Section, Group, MergeGroup,
    TimetableEntry, TimetableOverride, ClassCancellation
)
from .exceptions import (
    InvalidStudentContext, InvalidSemester, InvalidSection, InvalidGroup
)


def validate_student_context(
    semester_val: Any,
    section_val: Any,
    group_val: Optional[Any] = None
) -> Tuple[Semester, Section, Optional[Group]]:
    """
    Validates that the specified semester, section, and group combination actually exists.
    
    Raises InvalidSemester, InvalidSection, or InvalidGroup if invalid.
    """
    if not semester_val:
        raise InvalidSemester("Semester must be specified.")

    # 1. Resolve Semester
    if isinstance(semester_val, Semester):
        sem_obj = semester_val
    elif isinstance(semester_val, int) or (isinstance(semester_val, str) and str(semester_val).isdigit()):
        sem_obj = Semester.objects.filter(number=int(semester_val), is_active=True).first()
    else:
        # Match string like "5th Semester" or "Semester 5"
        sem_str = str(semester_val)
        import re
        m = re.search(r'\b([1-8])\b', sem_str)
        if m:
            sem_obj = Semester.objects.filter(number=int(m.group(1)), is_active=True).first()
        else:
            sem_obj = None

    if not sem_obj:
        raise InvalidSemester(f"Semester '{semester_val}' is invalid or inactive.")

    # 2. Resolve Section
    if not section_val:
        raise InvalidSection("Section must be specified.")

    if isinstance(section_val, Section):
        sec_obj = section_val
    else:
        sec_str = str(section_val).strip()
        sec_obj = Section.objects.filter(
            Q(name__iexact=sec_str) | Q(name__iexact=f"CSE-{sec_str}") | Q(name__iexact=f"{sem_obj.number}CSE{sec_str}"),
            semester=sem_obj
        ).first()

    if not sec_obj:
        raise InvalidSection(f"Section '{section_val}' is invalid for Semester {sem_obj.number}.")

    # 3. Resolve Group
    grp_obj = None
    if group_val is not None and str(group_val).strip() != "":
        if isinstance(group_val, Group):
            grp_obj = group_val
        else:
            grp_str = str(group_val).strip()
            grp_obj = Group.objects.filter(name__iexact=grp_str, section=sec_obj).first()

        if not grp_obj:
            raise InvalidGroup(f"Group '{group_val}' is invalid for Section '{sec_obj.name}'.")

    return sem_obj, sec_obj, grp_obj


def resolve_group_entry(
    semester: Semester,
    section: Section,
    group: Optional[Group],
    day: str,
    period: int,
    date_val: Optional[datetime.date] = None
) -> Tuple[Optional[TimetableEntry], Optional[TimetableOverride], bool]:
    """
    Resolves student timetable entry for a specific day and period.
    
    Order of evaluation:
    1. Date-specific TimetableOverride (if date_val is provided)
    2. Direct group/section TimetableEntry
    3. Shared MergeGroup TimetableEntry
    
    Returns: (timetable_entry, timetable_override, is_cancelled)
    """
    # 1. Check Date-Specific TimetableOverride
    if date_val:
        override = TimetableOverride.objects.filter(
            date=date_val,
            period=period,
            semester=semester
        ).filter(
            Q(section=section) | Q(section__isnull=True)
        ).select_related('subject', 'teacher', 'room').first()

        if override:
            return None, override, False

    # 2. Query Direct TimetableEntry with select_related for database efficiency
    query = TimetableEntry.objects.filter(
        semester=semester,
        day=day,
        period=period
    ).select_related('subject', 'teacher', 'room', 'section', 'group', 'merge_group', 'time_slot')

    # Direct Section/Group check
    direct_entries = list(query.filter(section=section))
    match_entry = None

    if group:
        # Prefer exact group match first
        match_entry = next((e for e in direct_entries if e.group_id == group.id), None)
        if not match_entry:
            # Fall back to full section entry (group is null)
            match_entry = next((e for e in direct_entries if e.group_id is None and e.merge_group_id is None), None)
    else:
        match_entry = next((e for e in direct_entries if e.merge_group_id is None), None)

    # 3. Check Shared MergeGroup membership if no direct entry found
    if not match_entry:
        merge_entries = query.filter(merge_group__isnull=False)
        for m_entry in merge_entries:
            mg = m_entry.merge_group
            if mg:
                # Check if group or section belongs to this merge group
                if group and mg.groups.filter(id=group.id).exists():
                    match_entry = m_entry
                    break
                elif not group and mg.groups.filter(section=section).exists():
                    match_entry = m_entry
                    break

    # 4. Check ClassCancellation
    is_cancelled = False
    if match_entry and date_val:
        is_cancelled = ClassCancellation.objects.filter(
            timetable_entry=match_entry,
            date=date_val
        ).exists()

    return match_entry, None, is_cancelled
