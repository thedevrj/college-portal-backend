from rest_framework import serializers
from django.db import models
import os
from .models import Affidavit, AffidavitFAQ, AffidavitGuidelines, SampleAffidavit


class AffidavitSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)

    class Meta:
        model = Affidavit
        fields = [
            "id",
            "tracking_id",
            "student_name",
            "roll_number",
            "enrollment_number",
            "program_name",
            "department",
            "department_name",
            "student_phone",
            "student_email",
            "parent_name",
            "parent_phone",
            "student_affidavit",
            "parent_affidavit",
            "status",
            "remarks",
            "submitted_on",
            "updated_on",
        ]
        read_only_fields = ["id", "tracking_id", "status", "remarks", "submitted_on", "updated_on"]

    def to_internal_value(self, data):
        # Support passing department slug or string instead of integer primary key
        if "department" in data and isinstance(data["department"], str) and not data["department"].isdigit():
            from apps.academics.models import Department
            dept_str = data["department"].strip()
            dept_obj = Department.objects.filter(models.Q(slug__iexact=dept_str) | models.Q(name__iexact=dept_str)).first()
            if dept_obj:
                data = data.copy()
                data["department"] = dept_obj.id
        return super().to_internal_value(data)

    def validate_student_phone(self, value):
        if not value.isdigit() or len(value) != 10 or value[0] not in "6789":
            raise serializers.ValidationError("Student phone number must be a valid 10-digit number.")
        return value

    def validate_parent_phone(self, value):
        if value and (not value.isdigit() or len(value) != 10 or value[0] not in "6789"):
            raise serializers.ValidationError("Parent phone number must be a valid 10-digit number.")
        return value

    def validate_student_email(self, value):
        value = value.strip().lower()
        return value


class AffidavitFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffidavitFAQ
        fields = ["id", "question", "answer", "order"]


class AffidavitGuidelinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffidavitGuidelines
        fields = ["id", "title", "content"]

class SampleAffidavitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleAffidavit
        fields = ["id", "title", "file", "affidavit_category"]
        read_only_fields = ["id"]
    
    def validate_file(self, value):
        allowed_extensions = [".pdf", ".doc", ".docx"]
        file_extension = os.path.splitext(value.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError("Only PDF and Word documents are allowed.")
        return value  
