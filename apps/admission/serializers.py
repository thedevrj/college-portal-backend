from rest_framework import serializers
from .models import (
    AdmissionSession,
    AdmissionStream,
    AdmissionProspectus,
    AdmissionNotice,
    RegistrationPortal,
    CounsellingPhase,
    MeritList,
    AdmissionCommitteeMember,
    AdmissionCommitteeMinutes,
)


class AdmissionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionSession
        fields = ["id", "session_name", "start_date", "end_date", "is_active"]


class AdmissionStreamSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = AdmissionStream
        fields = [
            "id",
            "session",
            "session_details",
            "name",
            "category",
            "category_display",
            "order",
            "is_active",
        ]


class AdmissionProspectusSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    file = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionProspectus
        fields = [
            "id",
            "session",
            "session_details",
            "category",
            "category_display",
            "title",
            "file",
            "upload_date",
        ]

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None


class AdmissionNoticeSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    file = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionNotice
        fields = [
            "id",
            "session",
            "session_details",
            "category",
            "category_display",
            "title",
            "file",
            "date_posted",
            "is_active",
        ]

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None


class RegistrationPortalSerializer(serializers.ModelSerializer):
    session_details = AdmissionSessionSerializer(source="session", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = RegistrationPortal
        fields = [
            "id",
            "session",
            "session_details",
            "category",
            "category_display",
            "portal_name",
            "url",
            "registration_start",
            "registration_end",
            "is_active",
        ]


class CounsellingPhaseSerializer(serializers.ModelSerializer):
    stream_details = AdmissionStreamSerializer(source="stream", read_only=True)

    class Meta:
        model = CounsellingPhase
        fields = [
            "id",
            "stream",
            "stream_details",
            "phase_name",
            "order",
            "is_active",
        ]


class MeritListSerializer(serializers.ModelSerializer):
    phase_details = CounsellingPhaseSerializer(source="phase", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    programme_name = serializers.CharField(source="programme.name", read_only=True)
    pdf_file = serializers.SerializerMethodField()

    class Meta:
        model = MeritList
        fields = [
            "id",
            "phase",
            "phase_details",
            "department",
            "department_name",
            "programme",
            "programme_name",
            "pdf_file",
            "upload_date",
        ]

    def get_pdf_file(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None


class AdmissionCommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionCommitteeMember
        fields = [
            "id",
            "name",
            "designation",
            "email",
            "order",
        ]


class AdmissionCommitteeMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = AdmissionCommitteeMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_private",
        ]

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None
