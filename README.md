# CSE SmartRoom — Department Timetable Locator & REST API Gateway

CSE SmartRoom is a real-time student-centric room and timetable locator for a Computer Science & Engineering department built with **Python, Django, Django REST Framework, and PostgreSQL**.

---

## Setup & Environment

1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and set PostgreSQL credentials:
   ```env
   USE_POSTGRES=False  # Set True for PostgreSQL production database
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=csesmartroom
   DB_USER=smartroom_user
   DB_PASSWORD=smartroom_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Run Complete Test Suite (101 Tests)**:
   ```bash
   python manage.py test timetable core
   ```

---

## Module 5: REST API Gateway (`/api/v1/`)

Module 5 provides versioned REST endpoints serving real-time student state, room occupancy, teacher locations, campus stats, metadata, and secure timetable downloads for Modules 6 & 7.

### Standard Response Format:

#### Success Response (HTTP 200):
```json
{
  "success": true,
  "data": { ... }
}
```

#### Error Response (HTTP 400 / 404 / 409 / 429):
```json
{
  "success": false,
  "error": {
    "code": "INVALIDSEMESTER",
    "message": "Semester '99' is invalid or inactive."
  }
}
```

---

### Endpoint Reference Table (`/api/v1/`)

| Method | Endpoint URL | Purpose | Service Used |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/student/current-class/` | Get student's current active class | `Module3: get_current_class()` |
| `GET` | `/api/v1/student/next-class/` | Get student's upcoming class | `Module3: get_next_class()` |
| `GET` | `/api/v1/student/state/` | Complete real-time student state | `Module3: get_student_timetable_state()` |
| `GET` | `/api/v1/student/schedule/` | Student day schedule | `Module3: get_day_schedule()` |
| `GET` | `/api/v1/rooms/<room>/status/` | Individual room status & class info | `Module4: get_room_status()` |
| `GET` | `/api/v1/rooms/free/` | Currently free rooms | `Module4: get_free_rooms()` |
| `GET` | `/api/v1/rooms/occupied/` | Currently occupied rooms | `Module4: get_occupied_rooms()` |
| `GET` | `/api/v1/rooms/status/` | All department room statuses | `Module4: get_all_room_statuses()` |
| `GET` | `/api/v1/rooms/<room>/schedule/` | Room complete day schedule | `Module4: get_room_day_schedule()` |
| `GET` | `/api/v1/rooms/<room>/next-free/` | Room next-free time calculation | `Module4: get_room_next_free()` |
| `GET` | `/api/v1/rooms/<room>/next-class/` | Room upcoming class | `Module4: get_room_next_class()` |
| `GET` | `/api/v1/rooms/search/` | Search rooms by number or type | `Module4: search_rooms()` |
| `GET` | `/api/v1/rooms/availability/` | Room continuous free/occupied windows | `Module4: get_room_availability()` |
| `GET` | `/api/v1/rooms/find-available/` | Find rooms free for complete interval | `Module4: find_available_rooms()` |
| `GET` | `/api/v1/teachers/search/` | Search faculty members | `Module4: search_teachers()` |
| `GET` | `/api/v1/teachers/<teacher>/location/` | Real-time teacher location & room | `Module4: get_teacher_current_location()` |
| `GET` | `/api/v1/teachers/<teacher>/next-class/` | Teacher upcoming class | `Module4: get_teacher_next_class()` |
| `GET` | `/api/v1/teachers/<teacher>/schedule/` | Teacher complete day schedule | `Module4: get_teacher_day_schedule()` |
| `GET` | `/api/v1/teachers/status/` | All active teacher location statuses | `Module4: get_all_teacher_statuses()` |
| `GET` | `/api/v1/campus/occupancy/` | Department campus occupancy stats | `Module4: get_campus_occupancy_state()` |
| `GET` | `/api/v1/metadata/semesters/` | Active semesters list for UI dropdowns | `Module1 DB Query` |
| `GET` | `/api/v1/metadata/sections/` | Active sections per semester | `Module1 DB Query` |
| `GET` | `/api/v1/metadata/groups/` | Active groups per section | `Module1 DB Query` |
| `GET` | `/api/v1/timetable/<sem>/<fmt>/` | Secure timetable download proxy | `Module2: download_timetable_view()` |
| `GET` | `/api/v1/health/` | API health check & DB ping | System status |
