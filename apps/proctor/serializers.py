from rest_framework import serializers
from .models import ProctorialBoardMember, ProctorialBoardMinutes, ProctorialBoardNotice


class ProctorialBoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorialBoardMember
        fields = "__all__"


class ProctorialBoardMinutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorialBoardMinutes
        fields = [
            "id",
            "meeting_title",
            "date_of_meeting",
            "file",
            "is_archived",
            "archive_date",
        ]


class ProctorialBoardNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProctorialBoardNotice
        fields = [
            "id",
            "title",
            "date",
            "file",
            "is_archived",
            "archive_date",
        ]
