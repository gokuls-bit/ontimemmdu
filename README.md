# CSE SmartRoom — Department Timetable Locator & Location Intelligence Engine

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

4. **Run Complete Test Suite**:
   ```bash
   python manage.py test timetable core
   ```

---

## Module 4: Global Location Intelligence Services

Module 4 provides campus-wide location intelligence for 80+ rooms/labs, 45+ faculty members, and ~2,100 students based on authoritative `Asia/Kolkata` backend time.

### Usage Examples:

```python
from core.services.location import (
    get_room_status, search_rooms, get_room_day_schedule, get_room_next_free,
    get_teacher_current_location, search_teachers, get_teacher_day_schedule,
    get_all_room_statuses, get_occupied_rooms, get_free_rooms, find_available_rooms,
    get_campus_occupancy_state, get_location_intelligence_state
)

# 1. "Who is in Room 357 right now?"
room_info = get_room_status("357")
print(room_info["status"])         # OCCUPIED / FREE / RESERVED / MAINTENANCE
print(room_info["current_class"])  # { "subject": "BCSE-501", "teacher": "Dr. Sharma", ... }

# 2. "Where is Dr. Sharma right now?"
teacher_info = get_teacher_current_location("Dr. Sharma")
print(teacher_info["status"])      # TEACHING / FREE / BREAK / LUNCH
print(teacher_info["room"])        # "357"

# 3. Genuinely Free Rooms Right Now
free_labs = get_free_rooms(room_type="LABORATORY")

# 4. Find Rooms Available for COMPLETE Time Interval (e.g. 11:00 - 13:00)
available = find_available_rooms(start_time="11:00", end_time="13:00", room_type="LABORATORY")

# 5. Global Campus Occupancy Overview
dashboard_state = get_campus_occupancy_state()
print(dashboard_state["total_rooms"], dashboard_state["occupied_rooms"], dashboard_state["utilization_percentage"])
```

---

## Module 3: Real-Time Decision Engine Services

Module 3 provides pure Python service functions to answer real-time student questions.

```python
from core.services.timetable.timetable_state import get_student_timetable_state

state = get_student_timetable_state(semester=5, section="5CSEA1", group="G1")
```

---

## Module 2: Timetable Importer & Download Service

### Management Command
Import any Excel (`.xlsx`) or JSON (`.json`) timetable file:
```bash
python manage.py import_timetable "smartroom/helpcse/cse_smartroom_3rd_5th_semester_complete.json"
```

### Download Endpoints
- **3rd Semester**: `GET /timetable/download/3rd/excel/` | `GET /timetable/download/3rd/json/`
- **4th Semester**: `GET /timetable/download/4th/excel/` | `GET /timetable/download/4th/json/`
- **5th Semester**: `GET /timetable/download/5th/excel/` | `GET /timetable/download/5th/json/`
