from rest_framework import serializers
from .models import (
    BoardOfManagementMember,
    BoardOfManagementMinutes,
    AcademicCouncilMember,
    AcademicCouncilMinutes,
    PlanningBoardMember,
    PlanningBoardMinutes,
    FinanceCommitteeMember,
    FinanceCommitteeMinutes,
)


# --- Board of Management (BoM) Serializers ---


class BoardOfManagementMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardOfManagementMember
        fields = "__all__"


class BoardOfManagementMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = BoardOfManagementMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_private",
        ]

    def get_file(self, obj):
        if obj.file:
            if obj.is_private:
                request = self.context.get('request')
                if request and not request.user.is_authenticated:
                    return None
            return obj.file.url
        return None


# --- Academic Council Serializers ---


class AcademicCouncilMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCouncilMember
        fields = "__all__"


class AcademicCouncilMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = AcademicCouncilMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_private",
        ]

    def get_file(self, obj):
        if obj.file:
            if obj.is_private:
                request = self.context.get('request')
                if request and not request.user.is_authenticated:
                    return None
            return obj.file.url
        return None


# --- Planning Board Serializers ---


class PlanningBoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningBoardMember
        fields = "__all__"


class PlanningBoardMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = PlanningBoardMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_private",
        ]

    def get_file(self, obj):
        if obj.file:
            if obj.is_private:
                request = self.context.get('request')
                if request and not request.user.is_authenticated:
                    return None
            return obj.file.url
        return None


# --- Finance Committee Serializers ---


class FinanceCommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceCommitteeMember
        fields = "__all__"


class FinanceCommitteeMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = FinanceCommitteeMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_private",
        ]

    def get_file(self, obj):
        if obj.file:
            if obj.is_private:
                request = self.context.get('request')
                if request and not request.user.is_authenticated:
                    return None
            return obj.file.url
        return None
