from django.contrib import admin
from .models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry,
    AcademicHoliday, ClassCancellation, TimetableOverride
)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'academic_year', 'is_active', 'created_at')
    list_filter = ('academic_year', 'is_active')
    search_fields = ('number', 'academic_year')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'capacity', 'created_at')
    list_filter = ('semester',)
    search_fields = ('name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'created_at')
    list_filter = ('section__semester', 'section')
    search_fields = ('name', 'section__name')


@admin.register(MergeGroup)
class MergeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    filter_horizontal = ('groups',)
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'short_name', 'subject_type', 'credits', 'semester')
    list_filter = ('subject_type', 'semester')
    search_fields = ('code', 'name', 'short_name')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'email', 'designation', 'department', 'is_active')
    list_filter = ('designation', 'department', 'is_active')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'building', 'floor', 'room_type', 'capacity', 'is_active')
    list_filter = ('building', 'room_type', 'floor', 'is_active')
    search_fields = ('room_number', 'building')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'period', 'start_time', 'end_time')
    list_filter = ('day', 'period')
    search_fields = ('day', 'period')
    ordering = ('day', 'period')


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = (
        'day', 'period', 'room', 'subject', 'teacher',
        'section', 'group', 'merge_group', 'class_type'
    )
    list_filter = ('day', 'period', 'room', 'teacher', 'semester', 'class_type')
    search_fields = ('subject__name', 'subject__code', 'teacher__first_name', 'teacher__last_name', 'room__room_number')
    autocomplete_fields = ['section', 'group', 'merge_group', 'subject', 'teacher', 'room', 'time_slot']


@admin.register(AcademicHoliday)
class AcademicHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ClassCancellation)
class ClassCancellationAdmin(admin.ModelAdmin):
    list_display = ('timetable_entry', 'date', 'reason', 'cancelled_by')
    list_filter = ('date',)
    search_fields = ('reason', 'cancelled_by')


@admin.register(TimetableOverride)
class TimetableOverrideAdmin(admin.ModelAdmin):
    list_display = ('date', 'period', 'semester', 'section', 'subject', 'room')
    list_filter = ('date', 'semester', 'class_type')
    search_fields = ('subject__code', 'room__room_number')

