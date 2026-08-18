# CSE SmartRoom — Department Timetable Locator & Database Services

CSE SmartRoom is a student-centric room and real-time timetable locator for the Computer Science & Engineering department built with **Python, Django, Django REST Framework, and PostgreSQL**.

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

4. **Run Unit Tests**:
   ```bash
   python manage.py test timetable core
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
- **3rd Semester**:
  - `GET /timetable/download/3rd/excel/`
  - `GET /timetable/download/3rd/json/`
- **4th Semester**:
  - `GET /timetable/download/4th/excel/`
  - `GET /timetable/download/4th/json/`
- **5th Semester**:
  - `GET /timetable/download/5th/excel/`
  - `GET /timetable/download/5th/json/`

---

## Security & Validation Architecture
- **ZIP Header Check**: Ensures `.xlsx` files start with magic bytes `PK\x03\x04`.
- **Macro & External Link Rejection**: Blocks `.xlsm`, `.xltm`, `vbaProject.bin`, and external workbook references.
- **Sanitization**: Strips control characters, normalizes whitespace, and truncates text.
- **Conflict Prevention**: Validates duplicate room bookings (`DUPLICATE_ROOM_BOOKING`) and missing attributes before database commit.
- **Transaction Rollback**: Uses `django.db.transaction.atomic()` to guarantee 100% atomic imports with full rollback on validation failure.
