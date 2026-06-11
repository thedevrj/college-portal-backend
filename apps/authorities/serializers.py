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
                if not request or not request.user.is_authenticated:
                    return None
                if not request.user.has_perm('authorities.view_boardofmanagementminutes'):
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
                if not request or not request.user.is_authenticated:
                    return None
                
                user = request.user
                if user.has_perm('authorities.view_academiccouncilminutes'):
                    return obj.file.url
                
                from apps.accounts.models import PortalRole
                if user.access_entries.filter(role__in=[PortalRole.DEAN, PortalRole.HOD], is_active=True).exists():
                    return obj.file.url
                    
                if hasattr(user, 'faculty_profile') and user.faculty_profile and getattr(user.faculty_profile, 'designation', '').lower() == 'professor':
                    return obj.file.url
                    
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
                if not request or not request.user.is_authenticated:
                    return None
                if not request.user.has_perm('authorities.view_planningboardminutes'):
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
                if not request or not request.user.is_authenticated:
                    return None
                if not request.user.has_perm('authorities.view_financecommitteeminutes'):
                    return None
            return obj.file.url
        return None
