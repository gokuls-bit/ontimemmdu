from rest_framework import serializers
from .models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    semester_details = SemesterSerializer(source='semester', read_only=True)

    class Meta:
        model = Section
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    section_name = serializers.ReadOnlyField(source='section.name')

    class Meta:
        model = Group
        fields = '__all__'


class MergeGroupSerializer(serializers.ModelSerializer):
    group_names = serializers.SerializerMethodField()

    class Meta:
        model = MergeGroup
        fields = '__all__'

    def get_group_names(self, obj):
        return [str(g) for g in obj.groups.all()]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Teacher
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = Room
        fields = '__all__'


class TimeSlotSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = TimeSlot
        fields = '__all__'


class TimetableEntrySerializer(serializers.ModelSerializer):
    semester_details = SemesterSerializer(source='semester', read_only=True)
    section_name = serializers.ReadOnlyField(source='section.name', default=None)
    group_name = serializers.ReadOnlyField(source='group.name', default=None)
    merge_group_name = serializers.ReadOnlyField(source='merge_group.name', default=None)
    subject_code = serializers.ReadOnlyField(source='subject.code')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')
    room_number = serializers.ReadOnlyField(source='room.room_number')
    day_display = serializers.ReadOnlyField(source='get_day_display')
    class_type_display = serializers.ReadOnlyField(source='get_class_type_display')

    class Meta:
        model = TimetableEntry
        fields = '__all__'

    def validate(self, attrs):
        instance = TimetableEntry(**attrs)
        if self.instance:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs
