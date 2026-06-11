from rest_framework import serializers
from .models import GlobalNotice


class GlobalNoticeListSerializer(serializers.ModelSerializer):
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = GlobalNotice
        # excluding heavy rich text payload for lists
        fields = "__all__"

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None


class GlobalNoticeDetailSerializer(serializers.ModelSerializer):
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = GlobalNotice
        fields = "__all__"

    def get_attachment(self, obj):
        if obj.attachment:
            return obj.attachment.url
        return None
