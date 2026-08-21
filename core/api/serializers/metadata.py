from rest_framework import serializers
from timetable.models import Semester, Section, Group


class GroupMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class SectionMetadataSerializer(serializers.ModelSerializer):
    groups = GroupMetadataSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'capacity', 'groups']


class SemesterMetadataSerializer(serializers.ModelSerializer):
    sections = SectionMetadataSerializer(many=True, read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'number', 'academic_year', 'is_active', 'sections']
