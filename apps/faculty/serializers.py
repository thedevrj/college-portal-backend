from rest_framework import serializers
from .models import Faculty

class FacultySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    cv_document = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = '__all__'

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_cv_document(self, obj):
        if obj.cv_document:
            return obj.cv_document.url
        return None