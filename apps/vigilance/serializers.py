from rest_framework import serializers
from .models import Complaint, ComplaintAttachment, FAQ, PolicyDocument, ComplaintActionLog

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'order']

class PolicyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocument
        fields = ['id', 'title', 'document_type', 'file', 'uploaded_at']

class ComplaintAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintAttachment
        fields = ['id', 'file', 'uploaded_at']

class ComplaintSerializer(serializers.ModelSerializer):
    attachments = ComplaintAttachmentSerializer(many=True, read_only=True)
    # Using ListField to handle multiple file uploads in a single request
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Complaint
        fields = [
            'tracking_id', 'name', 'email', 'phone', 'is_anonymous',
            'category', 'description', 'status', 'submitted_at', 'updated_at',
            'attachments', 'uploaded_files'
        ]
        read_only_fields = ['tracking_id', 'status', 'submitted_at', 'updated_at']

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        
        # Ensure complete privacy for anonymous complaints
        if validated_data.get('is_anonymous', False):
            validated_data['name'] = None
            validated_data['email'] = None
            validated_data['phone'] = None
            
        complaint = Complaint.objects.create(**validated_data)
        
        # Save all attached files
        for file in uploaded_files:
            ComplaintAttachment.objects.create(complaint=complaint, file=file)
            
        return complaint
