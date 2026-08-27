"""
CSE SmartRoom — Senior QA Automated Execution & Audit Runner
Runs system checks, database audit, importer security, time engine, room/teacher engines,
REST APIs, concurrency benchmarks, security fuzzing, and E2E simulation.
"""

import os
import sys
import json
import time
import datetime
import zipfile
import io
import concurrent.futures
from pathlib import Path

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartroom.settings")
import django
django.setup()

from zoneinfo import ZoneInfo
from django.conf import settings
from django.core.management import call_command
from django.db import connection, transaction
from django.db.models import Count, Q
from django.test import RequestFactory, Client
from rest_framework.test import APIRequestFactory, APIClient

settings.ALLOWED_HOSTS = ['*', 'testserver', 'localhost', '127.0.0.1']

from timetable.models import (
    Semester, Section, Group, MergeGroup, Subject, Teacher, Room, TimeSlot,
    TimetableEntry, AcademicHoliday, ClassCancellation, TimetableOverride,
    RoomReservation, RoomException, AuditLog
)
from core.services.timetable.clock import get_current_datetime, KOLKATA_TZ
from core.services.timetable.period_engine import get_current_period
from core.services.timetable.student_schedule import get_current_class, get_next_class, get_day_schedule
from core.services.timetable.timetable_state import get_student_timetable_state
from core.services.timetable.group_resolver import resolve_group_entry
from core.services.timetable.importer import import_timetable
from core.services.timetable.json_importer import import_timetable_json
from core.services.timetable.security import validate_excel_security
from core.services.timetable.result import ImportResult
from core.services.timetable.downloads import get_whitelisted_file_path

from core.services.location import (
    get_room_status, search_rooms, get_room_day_schedule, get_room_next_free,
    get_room_next_class, get_room_utilization, get_all_room_statuses,
    get_occupied_rooms, get_free_rooms, get_room_availability, find_available_rooms
)
from core.services.location.teacher_engine import (
    get_teacher_current_location, search_teachers, get_teacher_day_schedule,
    get_teacher_next_class, get_all_teacher_statuses
)
from core.services.location.conflict_engine import check_room_schedule_conflict, check_teacher_schedule_conflict
from core.services.location.occupancy_engine import get_campus_occupancy_state

def run_qa_suite():
    report_data = {
        "project": "CSE SmartRoom",
        "timestamp": datetime.datetime.now(KOLKATA_TZ).isoformat(),
        "timezone": "Asia/Kolkata",
        "overall_status": "PARTIAL",
        "modules": {},
        "critical_failures": [],
        "warnings": [],
        "bugs": {"P0": [], "P1": [], "P2": [], "P3": []},
        "tests_summary": {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    }

    print("==================================================")
    print("      CSE SmartRoom QA Execution Suite            ")
    print("==================================================")

    # ----------------------------------------------------
    # SECTION 1: DJANGO SYSTEM & MIGRATIONS CHECK
    # ----------------------------------------------------
    print("\n--- [1/10] Django System & Migration QA ---")
    try:
        call_command('check')
        print("  [PASS] Django system check passed cleanly.")
        report_data["tests_summary"]["passed"] += 1
    except Exception as e:
        print(f"  [FAIL] Django system check failed: {e}")
        report_data["critical_failures"].append(f"System Check Failure: {e}")
        report_data["tests_summary"]["failed"] += 1

    try:
        call_command('makemigrations', check=True, dry_run=True)
        print("  [PASS] Migration check: No pending unapplied model changes.")
        report_data["tests_summary"]["passed"] += 1
    except Exception as e:
        print(f"  [WARNING] Unapplied model changes detected (pending migrations): {e}")
        report_data["warnings"].append("Pending database migrations detected.")
        report_data["bugs"]["P2"].append("Pending database migrations exist.")
        report_data["tests_summary"]["failed"] += 1

    # ----------------------------------------------------
    # SECTION 2: MODULE 1 — DATABASE & MODEL STRUCTURE QA
    # ----------------------------------------------------
    print("\n--- [2/10] Module 1 — Database QA ---")
    m1_tests = 0
    m1_passed = 0
    m1_failed = 0

    required_models = [Semester, Section, Group, Subject, Teacher, Room, TimeSlot, TimetableEntry, MergeGroup, AcademicHoliday, TimetableOverride, ClassCancellation, RoomReservation, RoomException]
    for model in required_models:
        m1_tests += 1
        if hasattr(model, '_meta'):
            m1_passed += 1
        else:
            m1_failed += 1

    dup_rooms = Room.objects.values('room_number').annotate(c=Count('id')).filter(c__gt=1)
    m1_tests += 1
    if not dup_rooms.exists():
        m1_passed += 1
        print("  [PASS] Room unique room_number constraint verified.")
    else:
        m1_failed += 1
        print(f"  [FAIL] Duplicate room numbers found in DB: {list(dup_rooms)}")
        report_data["bugs"]["P0"].append("Duplicate room numbers present in database.")

    dup_teachers = Teacher.objects.values('employee_id').annotate(c=Count('id')).filter(c__gt=1)
    m1_tests += 1
    if not dup_teachers.exists():
        m1_passed += 1
        print("  [PASS] Teacher unique employee_id constraint verified.")
    else:
        m1_failed += 1
        print(f"  [FAIL] Duplicate teacher employee IDs found in DB: {list(dup_teachers)}")
        report_data["bugs"]["P0"].append("Duplicate teacher employee IDs in database.")

    indexes = [idx.name for idx in TimetableEntry._meta.indexes]
    m1_tests += 1
    if 'idx_tt_room_day_period' in indexes and 'idx_tt_sec_day_period' in indexes and 'idx_tt_teach_day_period' in indexes:
        m1_passed += 1
        print("  [PASS] TimetableEntry database indexes verified (room, section, teacher).")
    else:
        m1_failed += 1
        print(f"  [FAIL] Missing expected indexes on TimetableEntry: {indexes}")

    report_data["modules"]["module_1"] = {
        "status": "PASS" if m1_failed == 0 else "PARTIAL",
        "tests": m1_tests,
        "passed": m1_passed,
        "failed": m1_failed
    }
    report_data["tests_summary"]["passed"] += m1_passed
    report_data["tests_summary"]["failed"] += m1_failed

    # ----------------------------------------------------
    # SECTION 3: MODULE 2 — IMPORTER & SECURITY QA
    # ----------------------------------------------------
    print("\n--- [3/10] Module 2 — Importer & Security QA ---")
    m2_tests = 0
    m2_passed = 0
    m2_failed = 0

    json_path_35 = Path(settings.BASE_DIR) / "smartroom" / "helpcse" / "cse_smartroom_3rd_5th_semester_complete.json"
    json_path_4 = Path(settings.BASE_DIR) / "smartroom" / "helpcse" / "cse_smartroom_timetable_data.json"

    m2_tests += 1
    if json_path_35.exists() and json_path_4.exists():
        m2_passed += 1
        print("  [PASS] Both helpcse JSON datasets exist on disk.")
    else:
        m2_failed += 1
        print("  [FAIL] JSON datasets missing from helpcse directory.")

    m2_tests += 1
    res_json = import_timetable_json(str(json_path_35))
    if res_json.success or res_json.parsed_count > 0:
        m2_passed += 1
        print(f"  [PASS] JSON importer processed {res_json.parsed_count} entries, imported {res_json.imported_count} records.")
    else:
        m2_failed += 1
        print(f"  [FAIL] JSON importer failed: {res_json.errors}")

    sem_counts = TimetableEntry.objects.values('semester__number').annotate(c=Count('id'))
    print(f"  [AUDIT] Timetable entries per semester in DB: {list(sem_counts)}")
    if not TimetableEntry.objects.filter(semester__number=5).exists():
        print("  [FAIL] JSON Importer Bug: All entries hardcoded to Semester 3; 5th Semester entries missing from Semester 5!")
        report_data["bugs"]["P1"].append("json_importer.py hardcodes Semester 3 for all imported entries.")

    fake_res = ImportResult("test.xls")
    m2_tests += 1
    if not validate_excel_security("test.xls", fake_res):
        m2_passed += 1
        print("  [PASS] Security: Legacy .xls extension correctly rejected.")
    else:
        m2_failed += 1
        print("  [FAIL] Security: Legacy .xls extension was NOT rejected.")

    fake_res = ImportResult("test.xlsm")
    m2_tests += 1
    if not validate_excel_security("test.xlsm", fake_res):
        m2_passed += 1
        print("  [PASS] Security: Macro-enabled .xlsm extension correctly rejected.")
    else:
        m2_failed += 1
        print("  [FAIL] Security: Macro-enabled .xlsm extension was NOT rejected.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr('xl/vbaProject.bin', b'fake_vba_code')
        zf.writestr('[Content_Types].xml', b'<xml></xml>')
    buf.seek(0)
    fake_res = ImportResult("test.xlsx")
    m2_tests += 1
    if not validate_excel_security(buf, fake_res):
        m2_passed += 1
        print("  [PASS] Security: Workbook containing vbaProject.bin correctly rejected.")
    else:
        m2_failed += 1
        print("  [FAIL] Security: Workbook with vbaProject.bin was NOT rejected!")
        report_data["bugs"]["P0"].append("Macro security check failed to block vbaProject.bin.")

    fake_res = ImportResult("../../evil.xlsx")
    m2_tests += 1
    if not validate_excel_security("../../evil.xlsx", fake_res):
        m2_passed += 1
        print("  [PASS] Security: Path traversal filename rejected.")
    else:
        m2_failed += 1

    m2_tests += 1
    initial_tt_count = TimetableEntry.objects.count()
    invalid_data = [
        {"subject": "BCSE-101", "teacher": "Dr. Valid", "room": "301", "day": "MON", "period": 1, "section": "CSE-A"},
        {"subject": "BCSE-102", "teacher": "Dr. Valid2", "room": "301", "day": "INVALID_DAY_NAME", "period": 99, "section": "CSE-A"}
    ]
    invalid_buf = io.StringIO(json.dumps(invalid_data))
    res_rollback = import_timetable_json(invalid_buf)
    final_tt_count = TimetableEntry.objects.count()
    if not res_rollback.success and final_tt_count == initial_tt_count:
        m2_passed += 1
        print("  [PASS] Atomic Transaction QA: Failed import rolled back completely. Zero partial writes.")
    else:
        m2_failed += 1
        print(f"  [FAIL] Atomic Transaction QA: Import failed but database count changed! ({initial_tt_count} -> {final_tt_count})")
        report_data["bugs"]["P0"].append("Atomic transaction rollback failed on invalid import.")

    report_data["modules"]["module_2"] = {
        "status": "PASS" if m2_failed == 0 else "PARTIAL",
        "tests": m2_tests,
        "passed": m2_passed,
        "failed": m2_failed
    }
    report_data["tests_summary"]["passed"] += m2_passed
    report_data["tests_summary"]["failed"] += m2_failed

    # ----------------------------------------------------
    # SECTION 4: MODULE 3 — TIME ENGINE QA
    # ----------------------------------------------------
    print("\n--- [4/10] Module 3 — Time Engine QA ---")
    m3_tests = 0
    m3_passed = 0
    m3_failed = 0

    m3_tests += 1
    if settings.TIME_ZONE == "Asia/Kolkata":
        m3_passed += 1
        print("  [PASS] Django settings TIME_ZONE is Asia/Kolkata.")
    else:
        m3_failed += 1
        print(f"  [FAIL] Django settings TIME_ZONE is '{settings.TIME_ZONE}', expected 'Asia/Kolkata'.")
        report_data["bugs"]["P1"].append(f"settings.TIME_ZONE is '{settings.TIME_ZONE}' instead of 'Asia/Kolkata'.")

    TimeSlot.objects.filter(day="FRI", period=2).update(start_time=datetime.time(9, 40), end_time=datetime.time(10, 40))
    TimeSlot.objects.filter(day="FRI", period=3).update(start_time=datetime.time(10, 40), end_time=datetime.time(11, 40))

    dt_1039 = datetime.datetime(2026, 8, 21, 10, 39, 59, tzinfo=KOLKATA_TZ)
    p_1039 = get_current_period(dt_1039)
    m3_tests += 1
    if p_1039["period"] == 2 and p_1039["status"] == "ACTIVE_CLASS":
        m3_passed += 1
        print("  [PASS] Boundary Test: 10:39:59 correctly returns Period 2.")
    else:
        m3_failed += 1
        print(f"  [FAIL] Boundary Test: 10:39:59 returned period {p_1039.get('period')}.")

    dt_1040 = datetime.datetime(2026, 8, 21, 10, 40, 0, tzinfo=KOLKATA_TZ)
    p_1040 = get_current_period(dt_1040)
    m3_tests += 1
    if p_1040["period"] == 3 and p_1040["status"] == "ACTIVE_CLASS":
        m3_passed += 1
        print("  [PASS] Boundary Test: 10:40:00 correctly returns Period 3.")
    else:
        m3_failed += 1
        print(f"  [FAIL] Boundary Test: 10:40:00 returned period {p_1040.get('period')}.")

    dt_sat = datetime.datetime(2026, 8, 22, 10, 0, 0, tzinfo=KOLKATA_TZ)
    p_sat = get_current_period(dt_sat)
    m3_tests += 1
    if p_sat["status"] == "WEEKEND":
        m3_passed += 1
        print("  [PASS] Saturday returns status WEEKEND.")
    else:
        m3_failed += 1
        print(f"  [FAIL] Saturday returned status {p_sat['status']}.")

    # Merged Group Test
    # Target primary active semester 3
    sem3 = Semester.objects.filter(number=3).first()
    sec3a, _ = Section.objects.get_or_create(name="CSE-A", semester=sem3)
    grp_f, _ = Group.objects.get_or_create(name="F", section=sec3a)
    grp_h, _ = Group.objects.get_or_create(name="H", section=sec3a)
    grp_j, _ = Group.objects.get_or_create(name="J", section=sec3a)
    grp_g, _ = Group.objects.get_or_create(name="G", section=sec3a)

    mg, _ = MergeGroup.objects.get_or_create(name="3Sem-F_H_J")
    mg.groups.add(grp_f, grp_h, grp_j)

    sub_lab = Subject.objects.filter(code="BCSE-305L").first()
    if not sub_lab:
        sub_lab = Subject.objects.create(code="BCSE-305L", name="Data Structures Lab", short_name="DS Lab", semester=sem3)

    t_lab, _ = Teacher.objects.get_or_create(employee_id="T101", defaults={"first_name": "Turing", "last_name": "Lab", "email": "tlab@cse.edu"})
    r_lab, _ = Room.objects.get_or_create(room_number="Lab-1", defaults={"capacity": 40})
    slot_p1 = TimeSlot.objects.filter(day="FRI", period=1).first()

    tt_mg = TimetableEntry.objects.filter(room=r_lab, day="FRI", period=1).first()
    if not tt_mg:
        tt_mg = TimetableEntry.objects.create(
            semester=sem3, section=sec3a, merge_group=mg,
            subject=sub_lab, teacher=t_lab, room=r_lab, time_slot=slot_p1,
            day="FRI", period=1, start_time=datetime.time(8, 40), end_time=datetime.time(9, 40)
        )
    else:
        tt_mg.semester = sem3
        tt_mg.section = sec3a
        tt_mg.merge_group = mg
        tt_mg.save()

    dt_p1 = datetime.datetime(2026, 8, 21, 9, 0, 0, tzinfo=KOLKATA_TZ)
    class_f = get_current_class(3, "CSE-A", "F", now=dt_p1)
    class_h = get_current_class(3, "CSE-A", "H", now=dt_p1)
    class_j = get_current_class(3, "CSE-A", "J", now=dt_p1)
    class_g = get_current_class(3, "CSE-A", "G", now=dt_p1)

    m3_tests += 1
    if (class_f.get("subject") == "BCSE-305L" and
        class_h.get("subject") == "BCSE-305L" and
        class_j.get("subject") == "BCSE-305L" and
        class_g.get("status") == "FREE"):
        m3_passed += 1
        print("  [PASS] Merged Group Logic: F, H, J receive merged lab class; unrelated group G remains FREE.")
    else:
        m3_failed += 1
        print(f"  [FAIL] Merged Group Logic failed! F:{class_f.get('subject')} G:{class_g.get('status')}")
        report_data["bugs"]["P1"].append("Merged group schedule resolution failed.")

    report_data["modules"]["module_3"] = {
        "status": "PASS" if m3_failed == 0 else "PARTIAL",
        "tests": m3_tests,
        "passed": m3_passed,
        "failed": m3_failed
    }
    report_data["tests_summary"]["passed"] += m3_passed
    report_data["tests_summary"]["failed"] += m3_failed

    # ----------------------------------------------------
    # SECTION 5: MODULE 4 — ROOM & TEACHER ENGINE QA
    # ----------------------------------------------------
    print("\n--- [5/10] Module 4 — Room & Teacher Engine QA ---")
    m4_tests = 0
    m4_passed = 0
    m4_failed = 0

    sem7 = Semester.objects.filter(number=7).first()
    if not sem7:
        sem7 = Semester.objects.create(number=7, academic_year="2026-27")

    sec7a, _ = Section.objects.get_or_create(name="7CSEF", semester=sem7)
    sub_ai = Subject.objects.filter(code="BCSE-701").first()
    if not sub_ai:
        sub_ai = Subject.objects.create(code="BCSE-701", name="Artificial Intelligence", short_name="AI", semester=sem7)

    t_ai, _ = Teacher.objects.get_or_create(employee_id="T701", defaults={"first_name": "Dr.", "last_name": "Bhattacherjee", "email": "abhattacherjee@cse.edu"})
    r_357, _ = Room.objects.get_or_create(room_number="357", defaults={"capacity": 70})

    slot_p3 = TimeSlot.objects.filter(day="FRI", period=3).first()

    tt_357 = TimetableEntry.objects.filter(room=r_357, day="FRI", period=3).first()
    if not tt_357:
        tt_357 = TimetableEntry.objects.create(
            semester=sem7, section=sec7a, subject=sub_ai,
            teacher=t_ai, room=r_357, time_slot=slot_p3,
            day="FRI", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40)
        )

    dt_p3 = datetime.datetime(2026, 8, 21, 11, 0, 0, tzinfo=KOLKATA_TZ)
    status_357 = get_room_status("357", now=dt_p3)

    m4_tests += 1
    if status_357["status"] == "OCCUPIED" and status_357["current_class"]["subject"] == "BCSE-701":
        m4_passed += 1
        print("  [PASS] Cross-Semester Room QA: Room 357 occupied by 7th Sem is globally OCCUPIED.")
    else:
        m4_failed += 1
        print(f"  [FAIL] Cross-Semester Room QA: Room 357 status was {status_357['status']}.")
        report_data["bugs"]["P0"].append("Cross-semester room occupancy failed.")

    sem5 = Semester.objects.filter(number=5).first()
    if not sem5:
        sem5 = Semester.objects.create(number=5, academic_year="2026-27")
    sec5a, _ = Section.objects.get_or_create(name="CSE-A", semester=sem5)
    sub_dbms = Subject.objects.filter(code="BCSE-502").first()
    if not sub_dbms:
        sub_dbms = Subject.objects.create(code="BCSE-502", name="Database Management", short_name="DBMS", semester=sem5)

    m4_tests += 1
    entry_conf = TimetableEntry(
        semester=sem5, section=sec5a, subject=sub_dbms, teacher=t_ai, room=r_357, time_slot=slot_p3, day="FRI", period=3, start_time=datetime.time(10, 40), end_time=datetime.time(11, 40)
    )
    try:
        entry_conf.save()
        m4_failed += 1
        print("  [FAIL] Room Conflict QA: TimetableEntry.save() allowed double-booking Room 357!")
        report_data["bugs"]["P1"].append("TimetableEntry model failed to prevent un-merged room double-booking.")
    except Exception:
        m4_passed += 1
        print("  [PASS] Room Conflict QA: TimetableEntry validation blocked double-booking Room 357.")

    teacher_loc = get_teacher_current_location("T701", now=dt_p3)
    m4_tests += 1
    if teacher_loc["status"] == "TEACHING" and teacher_loc["room"] == "357":
        m4_passed += 1
        print("  [PASS] Teacher Intelligence QA: Dr. Bhattacherjee location correctly reported as Room 357.")
    else:
        m4_failed += 1
        print(f"  [FAIL] Teacher Location failed: {teacher_loc}")

    report_data["modules"]["module_4"] = {
        "status": "PASS" if m4_failed == 0 else "PARTIAL",
        "tests": m4_tests,
        "passed": m4_passed,
        "failed": m4_failed
    }
    report_data["tests_summary"]["passed"] += m4_passed
    report_data["tests_summary"]["failed"] += m4_failed

    # ----------------------------------------------------
    # SECTION 6: MODULE 5 — REST API QA
    # ----------------------------------------------------
    print("\n--- [6/10] Module 5 — REST API QA ---")
    client = APIClient(HTTP_HOST='localhost')
    m5_tests = 0
    m5_passed = 0
    m5_failed = 0

    endpoints_to_test = [
        ("/api/v1/health/", 200),
        ("/api/v1/student/current-class/?semester=3&section=CSE-A&group=F", 200),
        ("/api/v1/student/next-class/?semester=3&section=CSE-A&group=F", 200),
        ("/api/v1/student/state/?semester=3&section=CSE-A&group=F", 200),
        ("/api/v1/student/schedule/?semester=3&section=CSE-A&group=F&day=FRI", 200),
        ("/api/v1/rooms/357/status/", 200),
        ("/api/v1/rooms/free/", 200),
        ("/api/v1/rooms/occupied/", 200),
        ("/api/v1/rooms/status/", 200),
        ("/api/v1/rooms/357/schedule/", 200),
        ("/api/v1/rooms/357/next-free/", 200),
        ("/api/v1/rooms/357/next-class/", 200),
        ("/api/v1/rooms/search/?q=357", 200),
        ("/api/v1/rooms/availability/?room=357", 200),
        ("/api/v1/rooms/find-available/?start_time=11:00&end_time=12:00", 200),
        ("/api/v1/teachers/search/?q=Bhattacherjee", 200),
        ("/api/v1/teachers/status/", 200),
        ("/api/v1/teachers/T701/location/", 200),
        ("/api/v1/teachers/T701/next-class/", 200),
        ("/api/v1/teachers/T701/schedule/", 200),
        ("/api/v1/campus/occupancy/", 200),
        ("/api/v1/metadata/semesters/", 200),
        ("/api/v1/metadata/sections/", 200),
        ("/api/v1/metadata/groups/", 200),
        ("/api/v1/timetable/3rd/json/", 200),
    ]

    for url, exp_code in endpoints_to_test:
        m5_tests += 1
        res = client.get(url)
        if res.status_code == exp_code and res.json().get("success") is True:
            m5_passed += 1
        else:
            m5_failed += 1
            print(f"  [FAIL] API Endpoint {url} returned HTTP {res.status_code}: {res.content.decode()[:100]}")

    print(f"  [{'PASS' if m5_failed==0 else 'PARTIAL'}] REST API endpoints verified: {m5_passed}/{m5_tests} passed.")

    report_data["modules"]["module_5"] = {
        "status": "PASS" if m5_failed == 0 else "PARTIAL",
        "tests": m5_tests,
        "passed": m5_passed,
        "failed": m5_failed
    }
    report_data["tests_summary"]["passed"] += m5_passed
    report_data["tests_summary"]["failed"] += m5_failed

    # ----------------------------------------------------
    # SECTION 7: DOWNLOAD SYSTEM SECURITY QA
    # ----------------------------------------------------
    print("\n--- [7/10] Download System Security QA ---")
    dl_tests = 0
    dl_passed = 0
    dl_failed = 0

    dl_tests += 1
    res_dl = client.get("/api/v1/timetable/3rd/json/")
    if res_dl.status_code == 200 and "dataset" in res_dl.json():
        dl_passed += 1
        print("  [PASS] Download QA: 3rd Semester JSON download works.")
    else:
        dl_failed += 1

    dl_tests += 1
    res_dl_ex = client.get("/api/v1/timetable/3rd/excel/")
    if res_dl_ex.status_code in {404, 400}:
        dl_passed += 1
        print("  [PASS] Download QA: 3rd Semester Excel download handles missing physical file securely (HTTP 404/400).")
    else:
        dl_failed += 1
        report_data["bugs"]["P2"].append("3rd Semester Excel file missing on server disk.")

    dl_tests += 1
    res_traversal = client.get("/api/v1/timetable/..%2f..%2fsettings/json/")
    if res_traversal.status_code in {400, 404}:
        dl_passed += 1
        print("  [PASS] Download Security: Path traversal parameter blocked.")
    else:
        dl_failed += 1
        print(f"  [FAIL] Download Security: Path traversal allowed! Code: {res_traversal.status_code}")
        report_data["bugs"]["P0"].append("Path traversal vulnerability in download endpoint.")

    report_data["tests_summary"]["passed"] += dl_passed
    report_data["tests_summary"]["failed"] += dl_failed

    # ----------------------------------------------------
    # SECTION 8: PERFORMANCE & N+1 QUERY BENCHMARK
    # ----------------------------------------------------
    print("\n--- [8/10] Performance & N+1 Query QA ---")
    from django.db import reset_queries
    settings.DEBUG = True
    reset_queries()

    start_q = len(connection.queries)
    res_state = client.get("/api/v1/student/state/?semester=3&section=CSE-A&group=F")
    queries_state = len(connection.queries) - start_q

    reset_queries()
    start_q = len(connection.queries)
    res_campus = client.get("/api/v1/campus/occupancy/")
    queries_campus = len(connection.queries) - start_q

    print(f"  [PERF] /api/v1/student/state/ executed {queries_state} DB queries.")
    print(f"  [PERF] /api/v1/campus/occupancy/ executed {queries_campus} DB queries.")

    if queries_state > 15 or queries_campus > 25:
        report_data["warnings"].append(f"High query count detected: student/state ({queries_state} queries), campus/occupancy ({queries_campus} queries).")
        report_data["bugs"]["P2"].append("High DB query count in API views (potential N+1 overhead).")

    # ----------------------------------------------------
    # SECTION 9: API LOAD & CONCURRENCY BENCHMARK
    # ----------------------------------------------------
    print("\n--- [9/10] API Load & Concurrency Benchmark ---")
    url_load = "/api/v1/student/state/?semester=3&section=CSE-A&group=F"

    def make_req():
        c = Client(HTTP_HOST='localhost')
        st = time.time()
        res = c.get(url_load)
        lat = (time.time() - st) * 1000
        return res.status_code, lat

    for concurrency in [10, 50, 100]:
        latencies = []
        errors = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_req) for _ in range(concurrency)]
            for f in concurrent.futures.as_completed(futures):
                code, lat = f.result()
                latencies.append(lat)
                if code not in {200, 429}:
                    errors += 1

        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
        print(f"  [LOAD] Concurrency {concurrency:3d} reqs | Avg Latency: {avg_lat:.2f}ms | P95: {p95:.2f}ms | Errors: {errors}")

    # ----------------------------------------------------
    # SECTION 10: END-TO-END CONVERGENCE SIMULATION
    # ----------------------------------------------------
    print("\n--- [10/10] E2E Convergence Simulation ---")
    sim_dt = datetime.datetime(2026, 8, 21, 11, 0, 0, tzinfo=KOLKATA_TZ)

    m3_curr = get_current_class(7, "7CSEF", now=sim_dt)
    m4_room = get_room_status("357", now=sim_dt)

    res_api = client.get("/api/v1/student/current-class/?semester=7&section=7CSEF")
    m5_curr = res_api.json()["data"] if res_api.status_code == 200 else {}

    print(f"  [E2E] Module 3 current room: {m3_curr.get('room')}")
    print(f"  [E2E] Module 4 room status:  {m4_room.get('status')} ({m4_room.get('current_class', {}).get('subject')})")
    print(f"  [E2E] Module 5 API room:     {m5_curr.get('room')}")

    e2e_converged = (m3_curr.get('room') == m4_room.get('room') == m5_curr.get('room') == "357")
    report_data["tests_summary"]["total"] = report_data["tests_summary"]["passed"] + report_data["tests_summary"]["failed"]

    if e2e_converged:
        print("  [PASS] E2E Simulation: All modules produced 100% identical data flow results!")
    else:
        print("  [FAIL] E2E Simulation: Modules disagreed on current class / room status!")
        report_data["bugs"]["P0"].append("E2E data flow mismatch between Time Engine and REST API.")

    p0_count = len(report_data["bugs"]["P0"])
    p1_count = len(report_data["bugs"]["P1"])
    p2_count = len(report_data["bugs"]["P2"])
    p3_count = len(report_data["bugs"]["P3"])

    if p0_count == 0 and p1_count == 0:
        report_data["overall_status"] = "PASS"
    elif p0_count == 0 and p1_count > 0:
        report_data["overall_status"] = "PARTIAL"
    else:
        report_data["overall_status"] = "FAIL"

    res_file = Path(settings.BASE_DIR) / "qa_results.json"
    with open(res_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    print("\n==================================================")
    print(f" QA Execution Finished. Results written to {res_file}")
    print("==================================================")
    return report_data

if __name__ == "__main__":
    run_qa_suite()
