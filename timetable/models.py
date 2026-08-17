from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model providing created_at and updated_at timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Semester(TimeStampedModel):
    """Represents an academic semester in the CSE department."""
    number = models.PositiveSmallIntegerField(
        help_text=_("Semester number, e.g., 1 to 8")
    )
    academic_year = models.CharField(
        max_length=20,
        help_text=_("Academic session year, e.g., 2025-2026")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Designates whether this semester is currently active")
    )

    class Meta:
        ordering = ['number']
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'academic_year'],
                name='unique_semester_number_academic_year'
            )
        ]

    def __str__(self):
        return f"Semester {self.number} ({self.academic_year})"


class Section(TimeStampedModel):
    """Represents a section within a semester, e.g., CSE-A, CSE-B."""
    name = models.CharField(max_length=20, help_text=_("Section name, e.g., CSE-A"))
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    capacity = models.PositiveIntegerField(
        default=60,
        help_text=_("Maximum student capacity in this section")
    )

    class Meta:
        ordering = ['semester', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'semester'],
                name='unique_section_name_per_semester'
            )
        ]

    def __str__(self):
        return f"{self.name} (Sem {self.semester.number})"


class Group(TimeStampedModel):
    """Represents a subgroup inside a section, e.g., G1, G2, F, H, J."""
    name = models.CharField(max_length=20, help_text=_("Group name, e.g., G1, F"))
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='groups'
    )

    class Meta:
        ordering = ['section', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'section'],
                name='unique_group_name_per_section'
            )
        ]

    def __str__(self):
        return f"{self.section.name} - Group {self.name}"


class MergeGroup(TimeStampedModel):
    """
    Represents a merged set of groups from one or more sections sharing a class and room.
    Example: CSE-F + CSE-H + CSE-J combined into one lab or lecture session.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Descriptive name for merged group, e.g., CSE-F+H+J")
    )
    groups = models.ManyToManyField(
        Group,
        related_name='merge_groups',
        help_text=_("Component groups included in this merged group")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional notes or reasoning for merged group schedule")
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"Merged: {self.name}"


class Subject(TimeStampedModel):
    """Represents an academic subject/course taught in the department."""
    class SubjectType(models.TextChoices):
        THEORY = 'THEORY', _('Theory')
        LAB = 'LAB', _('Lab')
        TUTORIAL = 'TUTORIAL', _('Tutorial')
        ELECTIVE = 'ELECTIVE', _('Elective')

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Subject code, e.g., CS101, CS502")
    )
    name = models.CharField(max_length=150, help_text=_("Full subject title"))
    short_name = models.CharField(max_length=30, help_text=_("Short code/acronym, e.g., DBMS"))
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices,
        default=SubjectType.THEORY
    )
    credits = models.PositiveSmallIntegerField(default=3)
    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects'
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.short_name}"


class Teacher(TimeStampedModel):
    """Represents a faculty member/teacher in the CSE department."""
    employee_id = models.CharField(
        max_length=30,
        unique=True,
        help_text=_("Unique faculty employee ID")
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    designation = models.CharField(
        max_length=50,
        default="Assistant Professor",
        help_text=_("e.g. Assistant Professor, Associate Professor, Professor")
    )
    department = models.CharField(max_length=50, default="CSE")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


class Room(TimeStampedModel):
    """Represents a classroom, lab, or lecture hall."""
    class RoomType(models.TextChoices):
        LECTURE_HALL = 'LECTURE_HALL', _('Lecture Hall')
        LAB = 'LAB', _('Lab')
        TUTORIAL_ROOM = 'TUTORIAL_ROOM', _('Tutorial Room')
        AUDITORIUM = 'AUDITORIUM', _('Auditorium')

    room_number = models.CharField(
        max_length=30,
        unique=True,
        help_text=_("Room identifier, e.g., C-301, Lab-2")
    )
    building = models.CharField(
        max_length=100,
        default="Engineering Block C"
    )
    floor = models.IntegerField(default=3)
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.LECTURE_HALL
    )
    capacity = models.PositiveIntegerField(
        help_text=_("Seating/lab station capacity")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['room_number']

    def __str__(self):
        return f"{self.room_number} ({self.get_room_type_display()}, Cap: {self.capacity})"


class TimeSlot(TimeStampedModel):
    """Represents a standard schedule period during the week."""
    class DayChoices(models.TextChoices):
        MONDAY = 'MON', _('Monday')
        TUESDAY = 'TUE', _('Tuesday')
        WEDNESDAY = 'WED', _('Wednesday')
        THURSDAY = 'THU', _('Thursday')
        FRIDAY = 'FRI', _('Friday')
        SATURDAY = 'SAT', _('Saturday')
        SUNDAY = 'SUN', _('Sunday')

    day = models.CharField(max_length=3, choices=DayChoices.choices)
    period = models.PositiveSmallIntegerField(
        help_text=_("Period index, e.g., 1 to 8")
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day', 'period']
        constraints = [
            models.UniqueConstraint(
                fields=['day', 'period'],
                name='unique_timeslot_day_period'
            )
        ]

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': _("End time must be after start time.")})

    def __str__(self):
        return f"{self.get_day_display()} Period {self.period} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"


class TimetableEntry(TimeStampedModel):
    """
    Connects semester, section, group (or merge_group), subject, teacher, room, day, period, 
    start_time, end_time, and class_type.
    
    Includes database indexes for:
    - (room, day, period)
    - (section, day, period)
    - (teacher, day, period)
    """
    class ClassType(models.TextChoices):
        LECTURE = 'LECTURE', _('Lecture')
        LAB = 'LAB', _('Lab')
        TUTORIAL = 'TUTORIAL', _('Tutorial')

    class DayChoices(models.TextChoices):
        MONDAY = 'MON', _('Monday')
        TUESDAY = 'TUE', _('Tuesday')
        WEDNESDAY = 'WED', _('Wednesday')
        THURSDAY = 'THU', _('Thursday')
        FRIDAY = 'FRI', _('Friday')
        SATURDAY = 'SAT', _('Saturday')
        SUNDAY = 'SUN', _('Sunday')

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='timetable_entries'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries'
    )
    merge_group = models.ForeignKey(
        MergeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )
    day = models.CharField(max_length=3, choices=DayChoices.choices)
    period = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    class_type = models.CharField(
        max_length=20,
        choices=ClassType.choices,
        default=ClassType.LECTURE
    )

    class Meta:
        ordering = ['day', 'period', 'room']
        verbose_name_plural = "Timetable Entries"
        indexes = [
            models.Index(fields=['room', 'day', 'period'], name='idx_tt_room_day_period'),
            models.Index(fields=['section', 'day', 'period'], name='idx_tt_sec_day_period'),
            models.Index(fields=['teacher', 'day', 'period'], name='idx_tt_teach_day_period'),
        ]

    def save(self, *args, **kwargs):
        # Auto-sync day, period, start_time, end_time from time_slot if set
        if self.time_slot:
            self.day = self.time_slot.day
            self.period = self.time_slot.period
            self.start_time = self.time_slot.start_time
            self.end_time = self.time_slot.end_time

        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # 1. Target entity validation (Section/Group OR MergeGroup)
        if not self.section and not self.merge_group:
            raise ValidationError(
                _("A timetable entry must specify either a Section or a MergeGroup.")
            )

        if self.group and self.section and self.group.section != self.section:
            raise ValidationError(
                _("Group '{group}' does not belong to section '{section}'.").format(
                    group=self.group.name, section=self.section.name
                )
            )

        # Sync times from time_slot if present
        if self.time_slot:
            slot_day = self.time_slot.day
            slot_period = self.time_slot.period
        else:
            slot_day = self.day
            slot_period = self.period

        if not slot_day or slot_period is None:
            raise ValidationError(_("Day and period must be specified or derived from TimeSlot."))

        # 2. Room Collision Check
        # Enforce that a room cannot be occupied by multiple timetable entries during the same day/period
        room_conflicts = TimetableEntry.objects.filter(
            room=self.room,
            day=slot_day,
            period=slot_period
        )
        if self.pk:
            room_conflicts = room_conflicts.exclude(pk=self.pk)

        if room_conflicts.exists():
            conflict = room_conflicts.first()
            raise ValidationError(
                _("Room '{room}' is already occupied on {day} Period {period} by {subject} ({teacher}).").format(
                    room=self.room.room_number,
                    day=self.time_slot.get_day_display() if self.time_slot else slot_day,
                    period=slot_period,
                    subject=conflict.subject.short_name,
                    teacher=conflict.teacher.full_name if conflict.teacher else "No Teacher"
                )
            )

        # 3. Teacher Collision Check
        if self.teacher:
            teacher_conflicts = TimetableEntry.objects.filter(
                teacher=self.teacher,
                day=slot_day,
                period=slot_period
            )
            if self.pk:
                teacher_conflicts = teacher_conflicts.exclude(pk=self.pk)

            if teacher_conflicts.exists():
                conflict = teacher_conflicts.first()
                raise ValidationError(
                    _("Teacher '{teacher}' is already assigned to a class on {day} Period {period} in Room {room}.").format(
                        teacher=self.teacher.full_name,
                        day=self.time_slot.get_day_display() if self.time_slot else slot_day,
                        period=slot_period,
                        room=conflict.room.room_number
                    )
                )

        # 4. Section Collision Check (if single section entry without merge_group)
        if self.section and not self.merge_group and not self.group:
            section_conflicts = TimetableEntry.objects.filter(
                section=self.section,
                group__isnull=True,
                day=slot_day,
                period=slot_period
            )
            if self.pk:
                section_conflicts = section_conflicts.exclude(pk=self.pk)

            if section_conflicts.exists():
                conflict = section_conflicts.first()
                raise ValidationError(
                    _("Section '{section}' is already scheduled for a full-section class on {day} Period {period} in Room {room}.").format(
                        section=self.section.name,
                        day=self.time_slot.get_day_display() if self.time_slot else slot_day,
                        period=slot_period,
                        room=conflict.room.room_number
                    )
                )

    def __str__(self):
        target = self.merge_group.name if self.merge_group else f"{self.section.name}" + (f" ({self.group.name})" if self.group else "")
        return f"[{self.day} P{self.period}] {target} - {self.subject.short_name} @ {self.room.room_number}"
