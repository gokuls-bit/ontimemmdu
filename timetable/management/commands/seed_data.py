import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from timetable.models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)


class Command(BaseCommand):
    help = 'Seeds the database with CSE SmartRoom department dataset (2,100 students scale, 45 teachers, 80 rooms, semesters, slots, timetable entries)'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting database seeding for CSE SmartRoom..."))

        # 1. Semesters
        semesters = []
        for num in range(1, 9):
            sem, _ = Semester.objects.get_or_create(
                number=num,
                academic_year="2025-2026",
                defaults={'is_active': True}
            )
            semesters.append(sem)
        self.stdout.write(f"Created {len(semesters)} semesters (Sem 1 - Sem 8).")

        # 2. Sections & Groups (Targeting ~2,100 students scale: 35 sections x ~60 capacity = 2,100 students)
        sections = []
        groups = []
        for sem in semesters:
            for sec_letter in ['A', 'B', 'C', 'D']:
                sec, _ = Section.objects.get_or_create(
                    name=f"CSE-{sec_letter}",
                    semester=sem,
                    defaults={'capacity': 60}
                )
                sections.append(sec)
                # Create subgroups G1, G2, F, H, J for practicals/tutorials
                for grp_name in ['G1', 'G2', 'F', 'H', 'J']:
                    grp, _ = Group.objects.get_or_create(
                        name=grp_name,
                        section=sec
                    )
                    groups.append(grp)

        self.stdout.write(f"Created {len(sections)} sections and {len(groups)} subgroups (~2,100 total capacity).")

        # 3. Merge Groups (Example: CSE-F+H+J sharing one merged lab session)
        merge_groups = []
        for sec in sections[:8]:  # For first 8 sections
            grp_f = Group.objects.get(name='F', section=sec)
            grp_h = Group.objects.get(name='H', section=sec)
            grp_j = Group.objects.get(name='J', section=sec)
            
            mg, created = MergeGroup.objects.get_or_create(
                name=f"{sec.name}-F+H+J",
                defaults={'description': f"Merged lab group for {sec.name} subgroups F, H, and J"}
            )
            if created:
                mg.groups.add(grp_f, grp_h, grp_j)
            merge_groups.append(mg)
        self.stdout.write(f"Created {len(merge_groups)} merged groups.")

        # 4. Teachers (45 CSE Faculty members)
        designations = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
        first_names = [
            'Alan', 'Ada', 'Grace', 'Donald', 'Linus', 'Tim', 'Guido', 'Dennis', 'Ken', 'Barbara',
            'Margaret', 'John', 'Claude', 'Leslie', 'Geoffrey', 'Yann', 'Yoshua', 'Andrew', 'Fei-Fei', 'Demis',
            'Satya', 'Sundar', 'Arvind', 'Shantanu', 'Reshma', 'Padmasree', 'Anshul', 'Ravi', 'Meenakshi', 'Sanjay',
            'Rajesh', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Nisha', 'Deepak', 'Kavita', 'Suresh', 'Pooja',
            'Manish', 'Neha', 'Alok', 'Swati', 'Rohit'
        ]
        last_names = [
            'Turing', 'Lovelace', 'Hopper', 'Knuth', 'Torvalds', 'Berners-Lee', 'van Rossum', 'Ritchie', 'Thompson', 'Liskov',
            'Hamilton', 'McCarthy', 'Shannon', 'Lamport', 'Hinton', 'LeCun', 'Bengio', 'Ng', 'Li', 'Hassabis',
            'Nadella', 'Pichai', 'Krishna', 'Narayen', 'Saujani', 'Warrior', 'Sharma', 'Kumar', 'Sundaram', 'Patel',
            'Gupta', 'Singh', 'Verma', 'Deshmukh', 'Joshi', 'Chawla', 'Mehta', 'Narang', 'Reddy', 'Chaudhary',
            'Bansal', 'Agarwal', 'Saxena', 'Kapoor', 'Malhotra'
        ]

        teachers = []
        for i in range(45):
            emp_id = f"CSE-FAC-{101 + i}"
            fname = first_names[i]
            lname = last_names[i]
            desig = designations[i % len(designations)]
            t, _ = Teacher.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': f"{fname.lower()}.{lname.lower().replace(' ', '')}@cse.edu",
                    'designation': desig,
                    'department': 'CSE'
                }
            )
            teachers.append(t)
        self.stdout.write(f"Created {len(teachers)} teachers.")

        # 5. Rooms (80 Rooms across Engineering Block C and D)
        rooms = []
        # 40 Lecture Halls (C-101 to C-410)
        for floor in range(1, 5):
            for rnum in range(1, 11):
                room_no = f"C-{floor}{rnum:02d}"
                r, _ = Room.objects.get_or_create(
                    room_number=room_no,
                    defaults={
                        'building': 'Engineering Block C',
                        'floor': floor,
                        'room_type': Room.RoomType.LECTURE_HALL,
                        'capacity': 70
                    }
                )
                rooms.append(r)

        # 25 Labs (Lab-1 to Lab-25)
        for lnum in range(1, 26):
            room_no = f"Lab-{lnum}"
            r, _ = Room.objects.get_or_create(
                room_number=room_no,
                defaults={
                    'building': 'Engineering Block C',
                    'floor': (lnum % 4) + 1,
                    'room_type': Room.RoomType.LAB,
                    'capacity': 35
                }
            )
            rooms.append(r)

        # 15 Tutorial Rooms (T-1 to T-15)
        for tnum in range(1, 16):
            room_no = f"T-{tnum}"
            r, _ = Room.objects.get_or_create(
                room_number=room_no,
                defaults={
                    'building': 'Engineering Block D',
                    'floor': (tnum % 3) + 1,
                    'room_type': Room.RoomType.TUTORIAL_ROOM,
                    'capacity': 30
                }
            )
            rooms.append(r)
        self.stdout.write(f"Created {len(rooms)} rooms/labs.")

        # 6. TimeSlots (Monday to Friday, 8 periods per day)
        days = [
            TimeSlot.DayChoices.MONDAY,
            TimeSlot.DayChoices.TUESDAY,
            TimeSlot.DayChoices.WEDNESDAY,
            TimeSlot.DayChoices.THURSDAY,
            TimeSlot.DayChoices.FRIDAY
        ]
        start_hours = [9, 10, 11, 12, 14, 15, 16, 17]
        slots = []
        for d in days:
            for p_idx, hr in enumerate(start_hours, start=1):
                ts, _ = TimeSlot.objects.get_or_create(
                    day=d,
                    period=p_idx,
                    defaults={
                        'start_time': datetime.time(hr, 0),
                        'end_time': datetime.time(hr + 1, 0)
                    }
                )
                slots.append(ts)
        self.stdout.write(f"Created {len(slots)} weekly time slots.")

        # 7. Subjects (30 CSE core & elective subjects)
        subject_data = [
            ("CS101", "Programming in C", "C Prog", Subject.SubjectType.THEORY, 4, 1),
            ("CS101P", "Programming in C Lab", "C Lab", Subject.SubjectType.LAB, 2, 1),
            ("CS102", "Discrete Mathematics", "Disc Math", Subject.SubjectType.THEORY, 4, 1),
            ("CS201", "Data Structures & Algorithms", "DSA", Subject.SubjectType.THEORY, 4, 2),
            ("CS201P", "Data Structures Lab", "DSA Lab", Subject.SubjectType.LAB, 2, 2),
            ("CS202", "Object Oriented Programming", "OOP", Subject.SubjectType.THEORY, 4, 2),
            ("CS301", "Database Management Systems", "DBMS", Subject.SubjectType.THEORY, 4, 3),
            ("CS301P", "DBMS Lab", "DBMS Lab", Subject.SubjectType.LAB, 2, 3),
            ("CS302", "Computer Organization & Architecture", "COA", Subject.SubjectType.THEORY, 4, 3),
            ("CS303", "Operating Systems", "OS", Subject.SubjectType.THEORY, 4, 3),
            ("CS303P", "Operating Systems Lab", "OS Lab", Subject.SubjectType.LAB, 2, 3),
            ("CS401", "Computer Networks", "CN", Subject.SubjectType.THEORY, 4, 4),
            ("CS401P", "Computer Networks Lab", "CN Lab", Subject.SubjectType.LAB, 2, 4),
            ("CS402", "Design & Analysis of Algorithms", "DAA", Subject.SubjectType.THEORY, 4, 4),
            ("CS501", "Software Engineering", "SE", Subject.SubjectType.THEORY, 4, 5),
            ("CS502", "Theory of Computation", "TOC", Subject.SubjectType.THEORY, 4, 5),
            ("CS503", "Artificial Intelligence", "AI", Subject.SubjectType.THEORY, 4, 5),
            ("CS503P", "AI Lab", "AI Lab", Subject.SubjectType.LAB, 2, 5),
            ("CS601", "Compiler Design", "Compiler", Subject.SubjectType.THEORY, 4, 6),
            ("CS602", "Machine Learning", "ML", Subject.SubjectType.THEORY, 4, 6),
            ("CS602P", "Machine Learning Lab", "ML Lab", Subject.SubjectType.LAB, 2, 6),
            ("CS701", "Cloud Computing", "Cloud", Subject.SubjectType.ELECTIVE, 3, 7),
            ("CS702", "Cyber Security", "Security", Subject.SubjectType.ELECTIVE, 3, 7),
            ("CS703", "Big Data Analytics", "BigData", Subject.SubjectType.ELECTIVE, 3, 7),
            ("CS801", "Deep Learning", "DL", Subject.SubjectType.ELECTIVE, 3, 8),
            ("CS802", "Internet of Things", "IoT", Subject.SubjectType.ELECTIVE, 3, 8),
        ]
        subjects = []
        for code, name, short_name, stype, credits, sem_num in subject_data:
            sem_obj = Semester.objects.get(number=sem_num)
            sub, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'short_name': short_name,
                    'subject_type': stype,
                    'credits': credits,
                    'semester': sem_obj
                }
            )
            subjects.append(sub)
        self.stdout.write(f"Created {len(subjects)} subjects.")

        # 8. Timetable Entries Population (Sample non-conflicting schedule)
        entries_created = 0
        used_rooms = set()     # (room_id, day, period)
        used_teachers = set()  # (teacher_id, day, period)
        used_sections = set()  # (section_id, day, period)

        sec_idx = 0
        room_idx = 0
        teacher_idx = 0

        # Schedule theory lectures for sections
        for sec in sections:
            sem_subjects = [s for s in subjects if s.semester == sec.semester and s.subject_type == Subject.SubjectType.THEORY]
            for sub in sem_subjects:
                # Find open slot, room, teacher
                for ts in slots:
                    t = teachers[teacher_idx % len(teachers)]
                    r = rooms[room_idx % 40]  # Use lecture halls

                    key_r = (r.id, ts.day, ts.period)
                    key_t = (t.id, ts.day, ts.period)
                    key_s = (sec.id, ts.day, ts.period)

                    if key_r not in used_rooms and key_t not in used_teachers and key_s not in used_sections:
                        TimetableEntry.objects.create(
                            semester=sec.semester,
                            section=sec,
                            subject=sub,
                            teacher=t,
                            room=r,
                            time_slot=ts,
                            class_type=TimetableEntry.ClassType.LECTURE
                        )
                        used_rooms.add(key_r)
                        used_teachers.add(key_t)
                        used_sections.add(key_s)
                        entries_created += 1
                        room_idx += 1
                        teacher_idx += 1
                        break

        # Schedule merged lab entries
        for mg in merge_groups:
            first_group = mg.groups.first()
            sec = first_group.section if first_group else sections[0]
            lab_subject = Subject.objects.filter(semester=sec.semester, subject_type=Subject.SubjectType.LAB).first()
            if not lab_subject:
                lab_subject = subjects[1]  # fallback

            for ts in slots:
                t = teachers[teacher_idx % len(teachers)]
                r = rooms[40 + (room_idx % 25)]  # Use labs

                key_r = (r.id, ts.day, ts.period)
                key_t = (t.id, ts.day, ts.period)

                if key_r not in used_rooms and key_t not in used_teachers:
                    TimetableEntry.objects.create(
                        semester=sec.semester,
                        merge_group=mg,
                        subject=lab_subject,
                        teacher=t,
                        room=r,
                        time_slot=ts,
                        class_type=TimetableEntry.ClassType.LAB
                    )
                    used_rooms.add(key_r)
                    used_teachers.add(key_t)
                    entries_created += 1
                    room_idx += 1
                    teacher_idx += 1
                    break

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded database! Created {entries_created} timetable entries without conflicts."
        ))
