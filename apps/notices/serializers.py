from rest_framework import serializers
from .models import GlobalNotice


class GlobalNoticeListSerializer(serializers.ModelSerializer):
    attachment = serializers.SerializerMethodField()
    date_posted = serializers.SerializerMethodField()

    class Meta:
        model = GlobalNotice
        fields = "__all__"

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None

    def get_date_posted(self, obj):
        if obj.date_posted is None:
            return None
        # Coerce datetime → date safely (avoids DRF's AssertionError)
        value = obj.date_posted
        if hasattr(value, "date"):
            return value.date().isoformat()
        return str(value)


class GlobalNoticeDetailSerializer(serializers.ModelSerializer):
    attachment = serializers.SerializerMethodField()
    date_posted = serializers.SerializerMethodField()

    class Meta:
        model = GlobalNotice
        fields = "__all__"

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None

    def get_date_posted(self, obj):
        if obj.date_posted is None:
            return None
        value = obj.date_posted
        if hasattr(value, "date"):
            return value.date().isoformat()
        return str(value)
