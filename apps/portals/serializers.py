import os
from rest_framework import serializers
from .models import Grievance, GrievanceAttachment, GrievanceSignature


#  Allowed file types per form spec
ALLOWED_ATTACHMENT_EXTENSIONS = [".pdf", ".doc", ".docx"]
ALLOWED_SIGNATURE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


class GrievanceAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceAttachment
        fields = ["id", "file", "uploaded_at"]


class GrievanceSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceSignature
        fields = ["id", "image", "uploaded_at"]


class GrievanceSerializer(serializers.ModelSerializer):

    attachments = GrievanceAttachmentSerializer(many=True, read_only=True)
    signature = GrievanceSignatureSerializer(read_only=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
        help_text="Only PDF, DOC, DOCX files allowed.",
    )

    # Write — Form Field 17: Signature (Only jpg, jpeg, png)
    signature_image = serializers.ImageField(
        write_only=True,
        required=True,
        help_text="Only JPG, JPEG, PNG files allowed.",
    )

    class Meta:
        model = Grievance
        fields = [
            "tracking_id",
            "nature_of_grievance",
            "other_nature_of_grievance",
            "complainant_type",
            "other_complainant_type",
            "name_of_complainant",
            "aadhaar_number",
            "enrollment_id",
            "date_of_birth",
            "gender",
            "fathers_name",
            "mothers_name",
            "permanent_address",
            "state",
            "city",
            "pincode",
            "contact_number",
            "email",
            "complaint_text",
            "uploaded_files",
            "attachments",
            "signature_image",
            "signature",
            "declaration_accepted",
            "status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = [
            "tracking_id",
            "status",
            "submitted_at",
            "updated_at",
        ]

    #  Field-level validation

    def validate(self, data):
        complainant_type = data.get("complainant_type")
        other_complainant_type = data.get("other_complainant_type")
        nature_of_grievance = data.get("nature_of_grievance")
        other_nature_of_grievance = data.get("other_nature_of_grievance")

        errors = {}
        if complainant_type == "other" and not other_complainant_type:
            errors["other_complainant_type"] = (
                "Please specify the complainant type when 'Other' is selected."
            )

        if nature_of_grievance == "other" and not other_nature_of_grievance:
            errors["other_nature_of_grievance"] = (
                "Please specify the nature of grievance when 'Other' is selected."
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def validate_aadhaar_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "Aadhaar number must contain only digits."
            )
        if len(value) != 12:
            raise serializers.ValidationError(
                "Aadhaar number must be exactly 12 digits."
            )
        return value

    def validate_complaint_text(self, value):
        if len(value) > 500:
            raise serializers.ValidationError(
                "Complaint must not exceed 500 characters."
            )
        return value

    def validate_declaration_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must accept the declaration to submit the grievance."
            )
        return value

    def validate_uploaded_files(self, files):
        """Form Field 16: Only PDF, DOC, DOCX."""
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
                raise serializers.ValidationError(
                    f"'{f.name}' is not allowed. Only PDF, DOC, DOCX files are accepted."
                )
        return files

    def validate_signature_image(self, value):
        """Form Field 17: Only JPG, JPEG, PNG."""
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_SIGNATURE_EXTENSIONS:
            raise serializers.ValidationError(
                "Only JPG, JPEG, or PNG files are accepted for the signature."
            )
        return value

    #  Create

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        signature_image = validated_data.pop("signature_image", None)

        grievance = Grievance.objects.create(**validated_data)

        for f in uploaded_files:
            GrievanceAttachment.objects.create(grievance=grievance, file=f)

        if signature_image:
            GrievanceSignature.objects.create(
                grievance=grievance, image=signature_image
            )

        return grievance


class GrievanceStatusSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    nature_display = serializers.CharField(
        source="get_nature_of_grievance_display", read_only=True
    )

    class Meta:
        model = Grievance
        fields = [
            "tracking_id",
            "nature_of_grievance",
            "nature_display",
            "status",
            "status_display",
            "submitted_at",
            "updated_at",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Internal Complaints Committee (ICC) Serializers
# ─────────────────────────────────────────────────────────────────────────────
from .models import ICCComplaint, ICCAttachment, ICCSignature, ICCActionLog

class ICCActionLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_changed_to_display", read_only=True)
    date = serializers.DateTimeField(source="timestamp", read_only=True)
    description = serializers.CharField(source="action_description", read_only=True)
    status = serializers.CharField(source="status_changed_to", read_only=True)

    class Meta:
        model = ICCActionLog
        fields = ["status", "status_display", "date", "description"]


class ICCAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICCAttachment
        fields = ["id", "file", "uploaded_at"]


class ICCSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICCSignature
        fields = ["id", "image", "uploaded_at"]


class ICCComplaintSerializer(serializers.ModelSerializer):
    attachments = ICCAttachmentSerializer(many=True, read_only=True)
    signature = ICCSignatureSerializer(read_only=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        help_text="Only PDF files allowed.",
    )

    signature_image = serializers.ImageField(
        write_only=True,
        required=True,
        help_text="Only JPG, JPEG, PNG files allowed.",
    )

    class Meta:
        model = ICCComplaint
        fields = [
            "tracking_id",
            "nature_of_grievance",
            "other_nature_of_grievance",
            "name_of_complainant",
            "aadhaar_number",
            "enrollment_id",
            "date_of_birth",
            "gender",
            "fathers_name",
            "mothers_name",
            "permanent_address",
            "state",
            "city",
            "pincode",
            "contact_number",
            "email",
            "complaint_text",
            "uploaded_files",
            "attachments",
            "signature_image",
            "signature",
            "declaration_accepted",
            "status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["tracking_id", "status", "submitted_at", "updated_at"]

    def validate(self, data):
        nature_of_grievance = data.get("nature_of_grievance")
        other_nature_of_grievance = data.get("other_nature_of_grievance")

        errors = {}
        if nature_of_grievance == "other" and not other_nature_of_grievance:
            errors["other_nature_of_grievance"] = "Please specify the nature of grievance when 'Other' is selected."

        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def validate_aadhaar_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Aadhaar number must contain only digits.")
        if len(value) != 12:
            raise serializers.ValidationError("Aadhaar number must be exactly 12 digits.")
        return value

    def validate_complaint_text(self, value):
        if len(value) > 2000:
            raise serializers.ValidationError("Complaint must not exceed 2000 characters.")
        return value

    def validate_declaration_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the declaration to submit the grievance.")
        return value

    def validate_uploaded_files(self, files):
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in [".pdf"]:
                raise serializers.ValidationError(f"'{f.name}' is not allowed. Only PDF files are accepted.")
        return files

    def validate_signature_image(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_SIGNATURE_EXTENSIONS:
            raise serializers.ValidationError("Only JPG, JPEG, or PNG files are accepted for the signature.")
        return value

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        signature_image = validated_data.pop("signature_image", None)

        complaint = ICCComplaint.objects.create(**validated_data)

        for f in uploaded_files:
            ICCAttachment.objects.create(complaint=complaint, file=f)

        if signature_image:
            ICCSignature.objects.create(complaint=complaint, image=signature_image)

        return complaint


class ICCStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    nature_display = serializers.CharField(source="get_nature_of_grievance_display", read_only=True)
    history = ICCActionLogSerializer(source="action_logs", many=True, read_only=True)

    class Meta:
        model = ICCComplaint
        fields = [
            "tracking_id",
            "nature_of_grievance",
            "nature_display",
            "status",
            "status_display",
            "submitted_at",
            "updated_at",
            "history",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# SC/ST, OBC, Disable & Minority Discrimination Complaint Serializers
# ─────────────────────────────────────────────────────────────────────────────
from .models import (
    DiscriminationComplaint,
    DiscriminationAttachment,
    DiscriminationSignature,
    DiscriminationActionLog,
)

class DiscriminationActionLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_changed_to_display", read_only=True)
    date = serializers.DateTimeField(source="timestamp", read_only=True)
    description = serializers.CharField(source="action_description", read_only=True)
    status = serializers.CharField(source="status_changed_to", read_only=True)

    class Meta:
        model = DiscriminationActionLog
        fields = ["status", "status_display", "date", "description"]


class DiscriminationAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscriminationAttachment
        fields = ["id", "file", "uploaded_at"]


class DiscriminationSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscriminationSignature
        fields = ["id", "image", "uploaded_at"]


class DiscriminationComplaintSerializer(serializers.ModelSerializer):
    attachments = DiscriminationAttachmentSerializer(many=True, read_only=True)
    signature = DiscriminationSignatureSerializer(read_only=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        help_text="Only PDF files allowed.",
    )

    signature_image = serializers.ImageField(
        write_only=True,
        required=True,
        help_text="Only JPG, JPEG, PNG files allowed.",
    )

    class Meta:
        model = DiscriminationComplaint
        fields = [
            "tracking_id",
            "complaint_discrimination",
            "complaint_text",
            "enrollment_id",
            "roll_no",
            "school_name",
            "department_name",
            "course_name",
            "full_name",
            "aadhaar_number",
            "date_of_birth",
            "marital_status",
            "gender",
            "category_belonging",
            "fathers_name",
            "mothers_name",
            "contact_number",
            "email",
            "permanent_address",
            "state",
            "city",
            "pincode",
            "uploaded_files",
            "attachments",
            "signature_image",
            "signature",
            "declaration_accepted",
            "status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["tracking_id", "status", "submitted_at", "updated_at"]

    def validate_aadhaar_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Aadhaar number must contain only digits.")
        if len(value) != 12:
            raise serializers.ValidationError("Aadhaar number must be exactly 12 digits.")
        return value

    def validate_complaint_text(self, value):
        if len(value) > 2000:
            raise serializers.ValidationError("Complaint must not exceed 2000 characters.")
        return value

    def validate_declaration_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the declaration to submit the grievance.")
        return value

    def validate_uploaded_files(self, files):
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in [".pdf"]:
                raise serializers.ValidationError(f"'{f.name}' is not allowed. Only PDF files are accepted.")
        return files

    def validate_signature_image(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_SIGNATURE_EXTENSIONS:
            raise serializers.ValidationError("Only JPG, JPEG, or PNG files are accepted for the signature.")
        return value

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        signature_image = validated_data.pop("signature_image", None)

        complaint = DiscriminationComplaint.objects.create(**validated_data)

        for f in uploaded_files:
            DiscriminationAttachment.objects.create(complaint=complaint, file=f)

        if signature_image:
            DiscriminationSignature.objects.create(complaint=complaint, image=signature_image)

        return complaint


class DiscriminationStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    discrimination_display = serializers.CharField(source="get_complaint_discrimination_display", read_only=True)
    history = DiscriminationActionLogSerializer(source="action_logs", many=True, read_only=True)

    class Meta:
        model = DiscriminationComplaint
        fields = [
            "tracking_id",
            "complaint_discrimination",
            "discrimination_display",
            "status",
            "status_display",
            "submitted_at",
            "updated_at",
            "history",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Student Feedback Serializers
# ─────────────────────────────────────────────────────────────────────────────
from .models import (
    StudentFeedback,
    FeedbackAttachment,
    FeedbackSignature,
    FeedbackActionLog,
)

class FeedbackActionLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_changed_to_display", read_only=True)
    date = serializers.DateTimeField(source="timestamp", read_only=True)
    description = serializers.CharField(source="action_description", read_only=True)
    status = serializers.CharField(source="status_changed_to", read_only=True)

    class Meta:
        model = FeedbackActionLog
        fields = ["status", "status_display", "date", "description"]


class FeedbackAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackAttachment
        fields = ["id", "file", "uploaded_at"]


class FeedbackSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSignature
        fields = ["id", "image", "uploaded_at"]


class StudentFeedbackSerializer(serializers.ModelSerializer):
    attachments = FeedbackAttachmentSerializer(many=True, read_only=True)
    signature = FeedbackSignatureSerializer(read_only=True)

    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        help_text="Only PDF files allowed.",
    )

    signature_image = serializers.ImageField(
        write_only=True,
        required=True,
        help_text="Only JPG, JPEG, PNG files allowed.",
    )

    class Meta:
        model = StudentFeedback
        fields = [
            "tracking_id",
            "subject_of_feedback",
            "name_of_student",
            "aadhaar_number",
            "fathers_name",
            "mothers_name",
            "permanent_address",
            "state",
            "city",
            "pincode",
            "contact_number",
            "email",
            "course_name",
            "date_of_birth",
            "gender",
            "roll_no",
            "enrollment_no",
            "feedback_text",
            "uploaded_files",
            "attachments",
            "signature_image",
            "signature",
            "status",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["tracking_id", "status", "submitted_at", "updated_at"]

    def validate_aadhaar_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Aadhaar number must contain only digits.")
        if len(value) != 12:
            raise serializers.ValidationError("Aadhaar number must be exactly 12 digits.")
        return value

    def validate_feedback_text(self, value):
        if len(value) > 2000:
            raise serializers.ValidationError("Feedback must not exceed 2000 characters.")
        return value

    def validate_uploaded_files(self, files):
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in [".pdf"]:
                raise serializers.ValidationError(f"'{f.name}' is not allowed. Only PDF files are accepted.")
        return files

    def validate_signature_image(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_SIGNATURE_EXTENSIONS:
            raise serializers.ValidationError("Only JPG, JPEG, or PNG files are accepted for the signature.")
        return value

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])
        signature_image = validated_data.pop("signature_image", None)

        feedback = StudentFeedback.objects.create(**validated_data)

        for f in uploaded_files:
            FeedbackAttachment.objects.create(feedback=feedback, file=f)

        if signature_image:
            FeedbackSignature.objects.create(feedback=feedback, image=signature_image)

        return feedback


class FeedbackStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    subject_display = serializers.CharField(source="get_subject_of_feedback_display", read_only=True)
    history = FeedbackActionLogSerializer(source="action_logs", many=True, read_only=True)

    class Meta:
        model = StudentFeedback
        fields = [
            "tracking_id",
            "subject_of_feedback",
            "subject_display",
            "status",
            "status_display",
            "submitted_at",
            "updated_at",
            "history",
        ]
