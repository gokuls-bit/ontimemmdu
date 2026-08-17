# CSE SmartRoom — Module 1: Core Database & Data Model Architecture

## Overview
Module 1 establishes the foundational database architecture for **CSE SmartRoom**, a real-time student-centric room and timetable locator for a Computer Science & Engineering department. Built with **Python, Django, Django REST Framework, and PostgreSQL**, it supports scale requirements of **~2,100 students, 45 teachers, 80 rooms/labs, and 8 active semesters** without requiring database structural redesign.

---

## Entity Relationship & Schema Design

```
+------------------+         +------------------+         +------------------+
|     Semester     |<--------|     Section      |<--------|      Group       |
|  (num, yr, act)  | 1     N |   (name, cap)    | 1     N |    (name, sec)   |
+------------------+         +------------------+         +------------------+
         ^                            ^                            ^
         | 1                          | 1                          | N
         |                            |                            v
         |                            |                   +------------------+
         |                            |                   |    MergeGroup    |
         |                            |                   |   (name, grps)   |
         |                            |                   +------------------+
         |                            |                            ^
         +-------------------+        +--------------------+       |
                             |                             |       |
                             v                             v       v
+------------------+     +---------------------------------------------------+     +------------------+
|     Subject      |<----|                  TimetableEntry                   |---->|     Teacher      |
| (code, type, cr) | 1 N | (sem, sec, grp, merge, sub, teach, room, slot,    | N 1 | (emp_id, email,  |
+------------------+     |  day, period, start_time, end_time, class_type)   |     |  desig, dept)    |
                         +---------------------------------------------------+     +------------------+
                                        |                             |
                                      N | 1                         N | 1
                                        v                             v
                         +------------------+             +------------------+
                         |       Room       |             |     TimeSlot     |
                         | (no, bldg, cap)  |             |  (day, p, times) |
                         +------------------+             +------------------+
```

---

## Model Specifications & Fields

1. **`Semester`**: Represents academic term (`number`, `academic_year`, `is_active`). Unique constraint on `(number, academic_year)`.
2. **`Section`**: Department section e.g., CSE-A, CSE-B (`name`, `semester`, `capacity`). Unique constraint on `(name, semester)`.
3. **`Group`**: Practical/tutorial subgroup e.g. G1, G2, F, H, J (`name`, `section`). Unique constraint on `(name, section)`.
4. **`MergeGroup`**: Merged subgroups from one or more sections sharing a class and room (e.g. `CSE-F+H+J`). `ManyToMany` link to `Group`.
5. **`Subject`**: Academic course details (`code`, `name`, `short_name`, `subject_type`, `credits`, `semester`). Types: `THEORY`, `LAB`, `TUTORIAL`, `ELECTIVE`.
6. **`Teacher`**: Faculty profile (`employee_id`, `first_name`, `last_name`, `email`, `designation`, `department`). Unique employee ID and email.
7. **`Room`**: Shared physical venue (`room_number`, `building`, `floor`, `room_type`, `capacity`). Types: `LECTURE_HALL`, `LAB`, `TUTORIAL_ROOM`, `AUDITORIUM`.
8. **`TimeSlot`**: Weekly period definition (`day`, `period`, `start_time`, `end_time`). Unique constraint on `(day, period)`.
9. **`TimetableEntry`**: Main core timetable junction connecting all components with explicit validation.

---

## Database Performance & Indexes

The `TimetableEntry` model includes three high-performance compound database indexes:

- **`idx_tt_room_day_period`**: `Index(fields=['room', 'day', 'period'])`
  - Enables instant room availability check and prevents double-booking.
- **`idx_tt_sec_day_period`**: `Index(fields=['section', 'day', 'period'])`
  - Optimizes section timetable lookup and prevents section schedule conflicts.
- **`idx_tt_teach_day_period`**: `Index(fields=['teacher', 'day', 'period'])`
  - Facilitates real-time faculty locator queries and prevents teacher double-booking.

---

## Business Logic & Conflict Validation (`clean()`)

1. **Room Occupancy Conflict**: Hard validation prevents multiple timetable entries in the same room on the same day and period.
2. **Teacher Schedule Conflict**: Prevents a teacher from being assigned to multiple classes simultaneously.
3. **Section Schedule Conflict**: Prevents a section from being scheduled for two different classes in the same period unless using a `MergeGroup`.
4. **Target Entity Enforcement**: Requires either a valid `Section` or a `MergeGroup` for every timetable entry.
5. **Auto-Synchronization**: Automatically syncs `day`, `period`, `start_time`, and `end_time` from the associated `TimeSlot`.

---

## Environment & PostgreSQL Configuration

Database parameters are configured strictly through environment variables (`.env`):
- `USE_POSTGRES=True`
- `DB_ENGINE=django.db.backends.postgresql`
- `DB_NAME=csesmartroom`
- `DB_USER=smartroom_user`
- `DB_PASSWORD=smartroom_password`
- `DB_HOST=localhost`
- `DB_PORT=5432`

---

## Seed Benchmark Data & Test Scale

- **Semesters**: 8 (Sem 1 to Sem 8)
- **Sections**: 32 sections across semesters (~2,100 total student capacity)
- **Subgroups**: 160 subgroups (G1, G2, F, H, J)
- **Merged Groups**: 8 merged lab groups (e.g. `CSE-A-F+H+J`)
- **Teachers**: 45 CSE faculty members
- **Rooms/Labs**: 80 rooms (40 Lecture Halls, 25 Computer Labs, 15 Tutorial Rooms)
- **TimeSlots**: 40 weekly slots (Mon-Fri, 8 periods/day)
- **Subjects**: 26 CSE theory and lab courses
- **Fixtures**: `fixtures/sample_timetable.json`
