from rest_framework import serializers
from .models import GlobalNotice

class GlobalNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalNotice
        fields = '__all__'
