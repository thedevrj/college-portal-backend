from rest_framework import serializers
from .models import (
    COENotice,
    PHDPreSubmissionSeminar,
    RDCUNotice,
    MPHILVivaVoceDate,
    PHDVivaVoceDate,
)


class COENoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = COENotice
        fields = "__all__"


class PHDVivaVoceDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PHDVivaVoceDate
        fields = "__all__"


class MPHILVivaVoceDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MPHILVivaVoceDate
        fields = "__all__"


class PHDPreSubmissionSeminarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PHDPreSubmissionSeminar
        fields = "__all__"


class RDCUNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RDCUNotice
        fields = "__all__"
