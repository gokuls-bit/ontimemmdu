from rest_framework import serializers


class StudentQuerySerializer(serializers.Serializer):
    """Validates student context parameters: semester, section, group."""
    semester = serializers.CharField(required=True, help_text="Semester number or string, e.g. 5")
    section = serializers.CharField(required=True, help_text="Section name, e.g. 5CSEA1 or A")
    group = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Subgroup name, e.g. G1 or A")


class StudentScheduleQuerySerializer(StudentQuerySerializer):
    """Validates student day schedule query parameters including optional day."""
    day = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Day code, e.g. MON, TUE, Monday")


class CurrentClassSerializer(serializers.Serializer):
    status = serializers.CharField()
    semester = serializers.CharField()
    section = serializers.CharField()
    group = serializers.CharField(allow_null=True)
    period = serializers.IntegerField(allow_null=True)
    subject = serializers.CharField(allow_null=True)
    subject_name = serializers.CharField(allow_null=True)
    teacher = serializers.CharField(allow_null=True)
    room = serializers.CharField(allow_null=True)
    class_type = serializers.CharField(allow_null=True)
    start_time = serializers.CharField(allow_null=True)
    end_time = serializers.CharField(allow_null=True)
    minutes_elapsed = serializers.IntegerField()
    minutes_remaining = serializers.IntegerField()
    holiday_name = serializers.CharField(allow_null=True, required=False)


class NextClassSerializer(serializers.Serializer):
    status = serializers.CharField()
    period = serializers.IntegerField(allow_null=True)
    subject = serializers.CharField(allow_null=True)
    subject_name = serializers.CharField(allow_null=True)
    teacher = serializers.CharField(allow_null=True)
    room = serializers.CharField(allow_null=True)
    class_type = serializers.CharField(allow_null=True)
    start_time = serializers.CharField(allow_null=True)
    end_time = serializers.CharField(allow_null=True)
    minutes_until_start = serializers.IntegerField()
    intervening_break = serializers.DictField(allow_null=True, required=False)


class ScheduleEntrySerializer(serializers.Serializer):
    period = serializers.IntegerField()
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    teacher = serializers.CharField(allow_null=True)
    room = serializers.CharField(allow_null=True)
    class_type = serializers.CharField(allow_null=True)
    status = serializers.CharField()


class StudentStateSerializer(serializers.Serializer):
    server_time = serializers.CharField()
    timezone = serializers.CharField()
    date = serializers.CharField()
    day = serializers.CharField()
    day_name = serializers.CharField()
    status = serializers.CharField()
    student = serializers.DictField()
    current_period = serializers.DictField()
    current_class = CurrentClassSerializer()
    next_class = NextClassSerializer()
    today_schedule = ScheduleEntrySerializer(many=True)
