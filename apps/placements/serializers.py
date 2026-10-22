from rest_framework import serializers
from .models import PlacementNotice


class PlacementNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementNotice
        fields = "__all__"
