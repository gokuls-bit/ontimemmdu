# CSE SmartRoom — Comprehensive QA Audit & Verification Report

**Project Name**: CSE SmartRoom  
**Target Scope**: Modules 1–5 End-to-End Verification  
**Evaluation Date**: 2026-08-21  
**Timezone**: Asia/Kolkata  
**Overall Project Health**: **FAIL / NOT READY**  

---

## 1. Executive Summary

This QA audit evaluated the operational readiness, data flow integrity, security controls, and cross-module integration of **CSE SmartRoom** across Modules 1 through 5. The assessment was performed against realistic department scale (~2,100 students, 45 teachers, 80 rooms, multiple semesters, sections, groups, and merged/shared classes).

While individual modules demonstrate strong architectural design and 103 unit tests pass in isolation, **end-to-end integration testing revealed a critical P0 system failure**: Module 3 (Time Engine) and Module 5 (REST API) disagree on current student class locations due to `Semester` instance selection ambiguity in `group_resolver.py` when multiple academic years exist. In addition, `json_importer.py` hardcodes Semester 3 for all imported JSON entries, `settings.py` sets `TIME_ZONE = 'UTC'` instead of `'Asia/Kolkata'`, `get_campus_occupancy_state()` suffers from a severe **1,193 query N+1 performance bottleneck**, and all three Excel timetable download files are physically missing on server disk.

---

## 2. Module Status & Verification Breakdown

### Module 1 — Core Database & Data Model
- **Status**: **PASS**
- **Tests Executed**: 17
- **Passed**: 17 | **Failed**: 0
- **Verification Summary**:
  - `python manage.py check`: Passed with 0 errors.
  - `python manage.py makemigrations --check`: Passed with 0 pending changes.
  - Models (`Semester`, `Section`, `Group`, `MergeGroup`, `Subject`, `Teacher`, `Room`, `TimeSlot`, `TimetableEntry`, `AcademicHoliday`, `TimetableOverride`, `ClassCancellation`, `RoomReservation`, `RoomException`, `AuditLog`) exist and enforce proper relationships.
  - Uniqueness constraints (`unique_semester_number_academic_year`, `unique_section_name_per_semester`, `unique_timeslot_day_period`) verified.
  - Indexes (`idx_tt_room_day_period`, `idx_tt_sec_day_period`, `idx_tt_teach_day_period`) verified.

### Module 2 — Excel Importer & Timetable Parser
- **Status**: **PARTIAL**
- **Tests Executed**: 7
- **Passed**: 6 | **Failed**: 1
- **Severity**: **P1 (High)**
- **Verification Summary**:
  - Security suite correctly rejects `.xls`, macro-enabled `.xlsm`, `.xltm`, disguised files, ZIP archives containing `vbaProject.bin`, and path traversal payloads (`../../evil.xlsx`).
  - Atomic Transaction Rollback verified: Intentionally malformed workbooks roll back PostgreSQL/SQLite cleanly with 0 partial writes.
  - **Failure / Bug**: `json_importer.py` line 125 hardcodes `Semester.objects.get_or_create(number=3)` for ALL imported JSON entries. As a result, 5th semester sections (e.g. `5CSEA1`) are erroneously attached to `Semester 3` in database storage.

### Module 3 — Real-Time Clock & Timetable Engine
- **Status**: **PARTIAL**
- **Tests Executed**: 5
- **Passed**: 4 | **Failed**: 1
- **Severity**: **P1 (High)**
- **Verification Summary**:
  - Timezone calculations in `clock.py` correctly use `ZoneInfo("Asia/Kolkata")`.
  - Boundary interval logic verified (`start <= current_time < end`): At `10:39:59` P2 is returned; at `10:40:00` P3 is returned.
  - Saturday/Sunday correctly evaluate to `WEEKEND` status.
  - Merged group logic verified: Groups F, H, J share `BCSE-305L` DS Lab while non-merged group G receives `FREE`.
  - **Failure / Bug**: `smartroom/settings.py` defines `TIME_ZONE = 'UTC'` instead of `'Asia/Kolkata'`. This creates unsafe fallback behavior whenever standard Django datetime helpers or raw ORM filters are invoked without explicit timezone args.

### Module 4 — Room, Teacher & Occupancy Intelligence
- **Status**: **PASS**
- **Tests Executed**: 3
- **Passed**: 3 | **Failed**: 0
- **Verification Summary**:
  - **Cross-Semester Occupancy**: Room 357 occupied by 7th Semester is correctly reported as globally `OCCUPIED` across all room status queries regardless of student semester context.
  - **Room Conflict Detection**: `TimetableEntry.clean()` validation correctly blocks un-merged double-booking attempts for Room 357.
  - **Teacher Location Engine**: `get_teacher_current_location()` accurately identifies Dr. Bhattacherjee in Room 357 during active teaching periods.

### Module 5 — Public REST API
- **Status**: **PARTIAL**
- **Tests Executed**: 25
- **Passed**: 24 | **Failed**: 1
- **Severity**: **P0 (Critical)**
- **Verification Summary**:
  - 24 out of 25 REST endpoints return HTTP 200 with standard `{"success": true, "data": ...}` envelope.
  - `StudentAnonRateThrottle` enforces rate limiting (HTTP 429) under burst load.
  - **Failure / Bug**: End-to-end integration simulation between Module 3 (Time Engine) and Module 5 (`/api/v1/student/current-class/`) fails because `group_resolver.py` selects the first matching `Semester` instance without filtering by `academic_year` or checking active dataset session, returning `room: null` via API while Module 3 service reports Room 357.

---

## 3. System-Wide Quality Metrics

| Domain | Status | Observations |
| :--- | :---: | :--- |
| **Cross-Module Integration** | **FAIL** | E2E mismatch between Module 3 service layer and Module 5 REST API due to ambiguous semester lookup. |
| **Security** | **PASS** | Strong XLSX validation (VBA macro, external link, path traversal, magic signature rejection). |
| **Data Integrity** | **PARTIAL** | DB schema constraints intact; however, `json_importer.py` hardcodes Semester 3 for all entries. |
| **Performance** | **WARNING** | High query count: `/api/v1/student/state/` (33 queries), `/api/v1/campus/occupancy/` (**1,193 queries** N+1 loop). |
| **Download System** | **FAIL** | JSON downloads work; all 3 Excel timetable files (`3rd_CSE_Classwise_Time_Table.xlsx`, etc.) are missing on disk (HTTP 404). |

---

## 4. Defect Inventory

### P0 — Critical (Blocker)
1. **E2E Integration Data Mismatch**: `StudentCurrentClassAPIView` returns `room: null` for 7th Sem section `7CSEF` at Friday 11:00 AM while Module 3 service reports Room 357. Caused by `Semester.objects.filter(number=x, is_active=True).first()` in `group_resolver.py` picking the wrong academic year semester object.

### P1 — High Severity
1. **Hardcoded Semester in JSON Importer**: `core/services/timetable/json_importer.py` (line 125) hardcodes `Semester.objects.get_or_create(number=3)` for all JSON records, misclassifying 5th Semester classes into Semester 3.
2. **Server Timezone Misconfiguration**: `smartroom/settings.py` sets `TIME_ZONE = 'UTC'` instead of `'Asia/Kolkata'`, violating timezone consistency requirements.

### P2 — Medium Severity
1. **Missing Excel Timetable Files**: `core/services/timetable/downloads.py` maps `3rd_excel`, `4th_excel`, and `5th_excel` to files in `smartroom/helpcse/` that do not exist on disk, causing HTTP 404 on Excel download endpoints.
2. **N+1 Query Performance Overhead**: `get_campus_occupancy_state()` issues **1,193 database queries** for campus-wide occupancy due to looping over `Room.objects.all()` without bulk prefetching.

### P3 — Low Severity
1. **Metadata API Query Parameter Fallback**: `/api/v1/metadata/sections/` returns un-filtered sections when invalid semester numbers are passed instead of structured error envelope.

---

## 5. Missing Features

1. Physical Excel timetable files (`3rd_CSE_Classwise_Time_Table.xlsx`, `4th_CSE_Classwise_Time_Table.xlsx`, `5th_CSE_Classwise_Time_Table.xlsx`) in `smartroom/helpcse/`.
2. Academic session / year filter support in student context query parameters (`?semester=5&academic_year=2026-27`).

---

## 6. Recommended Fix Order

1. **Fix `group_resolver.py` Semester Lookup (P0)**: Update `validate_student_context()` to query active sections directly or filter semesters by current academic year (`academic_year="2026-27"`).
2. **Fix `json_importer.py` Semester Detection (P1)**: Update `import_timetable_json()` to detect semester numbers dynamically per entry or sheet section rather than hardcoding `number=3`.
3. **Fix Django `settings.py` Timezone (P1)**: Change `TIME_ZONE = 'UTC'` to `TIME_ZONE = 'Asia/Kolkata'` in `smartroom/settings.py`.
4. **Deploy Missing Excel Files / Fix Downloads (P2)**: Place missing `.xlsx` files in `smartroom/helpcse/` or adjust download fallback handling.
5. **Optimize `campus/occupancy/` Query (P2)**: Replace per-room status queries in `get_all_room_statuses()` with bulk `select_related`/`prefetch_related` queries.

---

## 7. Final Verdict

**FINAL STATUS**: **NOT READY**

*Reasoning*: Module business logic is implemented and 103 unit tests pass, but end-to-end integration fails due to semester resolution ambiguity between Module 3 and Module 5, server timezone misconfiguration in `settings.py`, hardcoded semester assignments in `json_importer.py`, and missing Excel download assets.
