from rest_framework import serializers
from .models import Resource, CommitteeMember, FAQ, EmergencyContact


class ResourceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Resource
        fields = ["id", "title", "category", "category_display", "description", "file", "published_on", "is_active"]


class CommitteeMemberSerializer(serializers.ModelSerializer):
    committee_type_display = serializers.CharField(source="get_committee_type_display", read_only=True)
    faculty_name = serializers.CharField(source="faculty.name", read_only=True, default=None)

    class Meta:
        model = CommitteeMember
        fields = ["id", "faculty", "faculty_name", "designation", "committee_type", "committee_type_display", "phone", "email", "display_order"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "display_order", "is_active"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ["id", "name", "role", "phone", "email", "available_hours", "display_order"]
