from rest_framework import serializers
from .models import (
    AdmissionSession,
    AdmissionUpdate,
    AdmissionBrochure,
    AdmissionSchedule,
    AdmissionContact,
    AdmissionLink,
    AdmissionMeritList,
)


class AdmissionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionSession
        fields = ["id", "session_name", "start_date", "end_date", "is_active"]


class AdmissionUpdateSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    departments_display = serializers.StringRelatedField(
        source="departments", many=True, read_only=True
    )
    programs_display = serializers.StringRelatedField(
        source="programs", many=True, read_only=True
    )

    class Meta:
        model = AdmissionUpdate
        fields = [
            "id",
            "session",
            "session_details",
            "title",
            "category",
            "category_display",
            "departments",
            "departments_display",
            "programs",
            "programs_display",
            "other_category_name",
            "description",
            "attachment",
            "date_posted",
        ]


class AdmissionMeritListSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    departments_display = serializers.StringRelatedField(
        source="departments", many=True, read_only=True
    )
    programs_display = serializers.StringRelatedField(
        source="programs", many=True, read_only=True
    )

    class Meta:
        model = AdmissionMeritList
        fields = [
            "id",
            "session",
            "session_details",
            "title",
            "category",
            "category_display",
            "departments",
            "departments_display",
            "programs",
            "programs_display",
            "other_category_name",
            "description",
            "attachment",
            "date_posted",
        ]


class AdmissionBrochureSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    departments_display = serializers.StringRelatedField(
        source="departments", many=True, read_only=True
    )
    programs_display = serializers.StringRelatedField(
        source="programs", many=True, read_only=True
    )

    class Meta:
        model = AdmissionBrochure
        fields = [
            "id",
            "session",
            "session_details",
            "title",
            "category",
            "category_display",
            "departments",
            "departments_display",
            "programs",
            "programs_display",
            "file",
            "upload_date",
        ]


class AdmissionScheduleSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    departments_display = serializers.StringRelatedField(
        source="departments", many=True, read_only=True
    )
    programs_display = serializers.StringRelatedField(
        source="programs", many=True, read_only=True
    )

    class Meta:
        model = AdmissionSchedule
        fields = [
            "id",
            "session",
            "session_details",
            "event_name",
            "category",
            "category_display",
            "departments",
            "departments_display",
            "programs",
            "programs_display",
            "event_date",
        ]


class AdmissionContactSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = AdmissionContact
        fields = [
            "id",
            "session",
            "session_details",
            "name",
            "designation",
            "category",
            "category_display",
            "email",
            "phone_number",
        ]


class AdmissionLinkSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = AdmissionLink
        fields = [
            "id",
            "session",
            "session_details",
            "title",
            "category",
            "category_display",
            "url",
        ]
