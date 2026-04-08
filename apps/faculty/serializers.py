from rest_framework import serializers
from .models import Faculty

class FacultySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Faculty
        fields = '__all__'

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return None