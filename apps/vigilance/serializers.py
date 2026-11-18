from rest_framework import serializers
from .models import (
    Complaint,
    ComplaintAttachment,
    FAQ,
    PolicyDocument,
    ComplaintActionLog,
)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "order"]


class PolicyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocument
        fields = ["id", "title", "document_type", "file", "uploaded_at"]


class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintAttachment
        fields = ["id", "file", "uploaded_at"]


from college_backend_portal.email_service import send_tracking_id_email


class ComplaintSerializer(serializers.ModelSerializer):
    attachments = ComplaintAttachmentSerializer(many=True, read_only=True)
    # Using ListField to handle multiple file uploads in a single request
    uploaded_files = serializers.ListField(
        child=serializers.FileField(
            max_length=100000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Complaint
        fields = [
            "tracking_id",
            "name",
            "email",
            "phone",
            "is_anonymous",
            "category",
            "description",
            "status",
            "others_status",
            "submitted_at",
            "updated_at",
            "attachments",
            "uploaded_files",
        ]
        read_only_fields = ["tracking_id", "status", "submitted_at", "updated_at"]

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files", [])

        # Ensure complete privacy for anonymous complaints
        if validated_data.get("is_anonymous", False):
            validated_data["name"] = None
            validated_data["email"] = None
            validated_data["phone"] = None

        complaint = Complaint.objects.create(**validated_data)

        # Save all attached files
        for file in uploaded_files:
            ComplaintAttachment.objects.create(complaint=complaint, file=file)

        if not complaint.is_anonymous and complaint.email and complaint.tracking_id:
            send_tracking_id_email(
                to_email=complaint.email,
                recipient_name=complaint.name or "Complainant",
                tracking_id=complaint.tracking_id,
                portal_name="Vigilance Cell",
                portal_slug="vigilance",
                category=complaint.get_category_display(),
                initial_status=complaint.get_status_display(),
                submitted_at=complaint.submitted_at,
            )

        return complaint


class ComplaintStatusUpdateSerializer(serializers.ModelSerializer):
    notify_user = serializers.BooleanField(default=True, required=False)
    remarks = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = Complaint
        fields = ["status", "notify_user", "remarks"]

    def validate(self, attrs):
        unexpected_fields = set(self.initial_data) - {"status", "notify_user", "remarks"}
        if unexpected_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be changed through this endpoint."
                    for field in unexpected_fields
                }
            )
        return attrs
