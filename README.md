# CSE SmartRoom — Department Timetable Locator & Decision Engine

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

## Module 3: Real-Time Decision Engine Services

Module 3 provides pure Python service functions to answer real-time student questions based on an authoritative `Asia/Kolkata` backend clock.

### Usage Examples:

```python
from core.services.timetable.timetable_state import get_student_timetable_state
from core.services.timetable.student_schedule import get_current_class, get_next_class, get_day_schedule

# 1. Consolidated Student Timetable State
state = get_student_timetable_state(
    semester=5,
    section="5CSEA1",
    group="G1"
)
print(state["current_class"])
print(state["next_class"])
print(state["today_schedule"])

# 2. Current Class
curr = get_current_class(semester=5, section="5CSEA1", group="G1")

# 3. Next Class (with intervening break detection & minutes until start)
nxt = get_next_class(semester=5, section="5CSEA1", group="G1")

# 4. Complete Day Schedule
day_sched = get_day_schedule(semester=5, section="5CSEA1", group="G1")
```

---

## Module 2: Timetable Importer & Download Service

### Management Command
Import any Excel (`.xlsx`) or JSON (`.json`) timetable file into the Django/PostgreSQL database:
```bash
python manage.py import_timetable "smartroom/helpcse/cse_smartroom_3rd_5th_semester_complete.json"
```

### Download Endpoints
Secure download URLs using server-side explicit whitelisting:
- **3rd Semester**: `GET /timetable/download/3rd/excel/` | `GET /timetable/download/3rd/json/`
- **4th Semester**: `GET /timetable/download/4th/excel/` | `GET /timetable/download/4th/json/`
- **5th Semester**: `GET /timetable/download/5th/excel/` | `GET /timetable/download/5th/json/`
