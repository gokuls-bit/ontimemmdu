# CSE SmartRoom — Department Timetable Locator & Administrative Control Center

CSE SmartRoom is a real-time student-centric room locator, timetable decision engine, and administrative control center for a Computer Science & Engineering department built with **Python, Django, Django REST Framework, PostgreSQL, React, and Vite**.

---

## Complete 7-Module Architecture Stack

```text
PostgreSQL Database
     ↓
Module 1 — Database & Core Data Foundation (Models, Constraints, Indexes)
     ↓
Module 2 — Excel / JSON Timetable Security Importer & Multi-Pass Validator
     ↓
Module 3 — Real-Time Time & Student Timetable Decision Engine
     ↓
Module 4 — Global Location Intelligence & Campus Occupancy Engine
     ↓
Module 5 — Unified Versioned REST API Gateway (/api/v1/...)
     ↓
Module 6 — Mobile-First Student-Facing React Application
     ↓
Module 7 — Administrative Control Center (RBAC, Alterations, Emergency Room Change, Audit Ledger)
```

---

## Setup & Execution

1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate
   ```

2. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Run Full Test Suite (109 Unit Tests)**:
   ```bash
   python manage.py test timetable core
   ```

4. **Launch Development Server**:
   ```bash
   python manage.py runserver 8000
   ```
   Open `http://127.0.0.1:8000/` in browser to access both the Student App and Admin Control Center.

---

## Module 7: Administrative Control Center (`/api/v1/admin/`)

| Method | Endpoint URL | Purpose | Service Used |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/admin/dashboard/` | Administrative dashboard metrics & department occupancy | `Module 4: get_campus_occupancy_state()` |
| `GET` | `/api/v1/admin/timetable/` | Administrative timetable viewer with multi-filters | `Module 1 DB Query` |
| `GET`/`POST` | `/api/v1/admin/alterations/` | List pending alterations / Create date-specific override | `Module 7: create_timetable_alteration()` |
| `POST` | `/api/v1/admin/alterations/<id>/approve/` | Atomically approve alteration after re-validating conflicts | `Module 7: approve_timetable_alteration()` |
| `POST` | `/api/v1/admin/emergency-room-change/` | Emergency room change wizard | `Module 7: emergency_room_change()` |
| `POST` | `/api/v1/admin/cancellations/` | Cancel single class instance on specific date | `Module 7: cancel_class_instance()` |
| `POST` | `/api/v1/admin/rooms/maintenance/` | Create room maintenance closure (blocks availability) | `Module 7: create_room_maintenance()` |
| `GET` | `/api/v1/admin/audit/` | View append-only audit history log | `Module 7: AuditLog Query` |
