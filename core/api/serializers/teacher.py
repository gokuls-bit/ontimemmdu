from rest_framework import serializers


class TeacherSearchQuerySerializer(serializers.Serializer):
    """Validates teacher search query string."""
    q = serializers.CharField(required=True, help_text="Search string for teacher name or employee ID")


class TeacherLocationSerializer(serializers.Serializer):
    teacher = serializers.CharField()
    employee_id = serializers.CharField()
    designation = serializers.CharField()
    department = serializers.CharField()
    status = serializers.CharField()
    room = serializers.CharField(allow_null=True)
    semester = serializers.CharField(allow_null=True)
    section = serializers.CharField(allow_null=True)
    group = serializers.CharField(allow_null=True)
    subject = serializers.CharField(allow_null=True)
    subject_name = serializers.CharField(allow_null=True)
    start_time = serializers.CharField(allow_null=True)
    end_time = serializers.CharField(allow_null=True)
    minutes_remaining = serializers.IntegerField()
    next_class = serializers.DictField(allow_null=True, required=False)


class TeacherScheduleEntrySerializer(serializers.Serializer):
    period = serializers.IntegerField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    status = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    room = serializers.CharField(allow_null=True)
    section = serializers.CharField(allow_null=True)
