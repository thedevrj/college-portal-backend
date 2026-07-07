from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        try:
            profile = getattr(user, 'portal_profile', None)
            token['force_password_change'] = profile.force_password_change if profile else False
        except Exception:
            token['force_password_change'] = False
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom data to response
        try:
            profile = getattr(self.user, 'portal_profile', None)
            data['force_password_change'] = profile.force_password_change if profile else False
        except Exception:
            data['force_password_change'] = False
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def validate_new_password(self, value):
        import re
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&* etc).")
        return value
