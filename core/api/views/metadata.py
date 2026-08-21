from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from timetable.models import Semester, Section, Group
from core.api.serializers import SemesterMetadataSerializer, SectionMetadataSerializer, GroupMetadataSerializer


class MetadataSemestersAPIView(APIView):
    """GET /api/v1/metadata/semesters/"""
    permission_classes = [AllowAny]

    def get(self, request):
        semesters = Semester.objects.filter(is_active=True).prefetch_related('sections__groups')
        serializer = SemesterMetadataSerializer(semesters, many=True)
        return Response(serializer.data)


class MetadataSectionsAPIView(APIView):
    """GET /api/v1/metadata/sections/"""
    permission_classes = [AllowAny]

    def get(self, request):
        semester_num = request.query_params.get('semester')
        sections = Section.objects.all().prefetch_related('groups')
        if semester_num:
            sections = sections.filter(semester__number=semester_num)

        serializer = SectionMetadataSerializer(sections, many=True)
        return Response(serializer.data)


class MetadataGroupsAPIView(APIView):
    """GET /api/v1/metadata/groups/"""
    permission_classes = [AllowAny]

    def get(self, request):
        section_id = request.query_params.get('section')
        groups = Group.objects.all()
        if section_id:
            groups = groups.filter(section_id=section_id)

        serializer = GroupMetadataSerializer(groups, many=True)
        return Response(serializer.data)
