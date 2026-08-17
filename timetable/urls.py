from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from .models import (
    Semester, Section, Group, MergeGroup,
    Subject, Teacher, Room, TimeSlot, TimetableEntry
)
from .serializers import (
    SemesterSerializer, SectionSerializer, GroupSerializer, MergeGroupSerializer,
    SubjectSerializer, TeacherSerializer, RoomSerializer, TimeSlotSerializer, TimetableEntrySerializer
)


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class MergeGroupViewSet(viewsets.ModelViewSet):
    queryset = MergeGroup.objects.all()
    serializer_class = MergeGroupSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class TimetableEntryViewSet(viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.select_related(
        'semester', 'section', 'group', 'merge_group',
        'subject', 'teacher', 'room', 'time_slot'
    ).all()
    serializer_class = TimetableEntrySerializer
    filterset_fields = ['semester', 'section', 'room', 'teacher', 'day', 'period', 'class_type']


router = DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'merge-groups', MergeGroupViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'timetable-entries', TimetableEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
