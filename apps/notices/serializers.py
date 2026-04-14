from rest_framework import serializers
from .models import GlobalNotice

class GlobalNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalNotice
        # excluding heavy rich text payload for lists
        exclude = ('attachment','link',)

class GlobalNoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalNotice
        fields = '__all__'
