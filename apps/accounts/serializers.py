from rest_framework import serializers
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        try:
            profile = getattr(user, "portal_profile", None)
            token["force_password_change"] = (
                profile.force_password_change if profile else False
            )
        except Exception:
            token["force_password_change"] = False
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add custom data to response
        try:
            profile = getattr(self.user, "portal_profile", None)
            data["force_password_change"] = (
                profile.force_password_change if profile else False
            )
        except Exception:
            data["force_password_change"] = False
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)

    new_password = serializers.CharField(required=True, write_only=True)

    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        # Check old password
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct."}
            )

        # Check password confirmation
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "New password and confirm password do not match."}
            )

        # Minimum 8 characters
        if len(new_password) < 8:
            raise serializers.ValidationError(
                {"new_password": "Password must be at least 8 characters long."}
            )

        # At least one uppercase letter
        if not re.search(r"[A-Z]", new_password):
            raise serializers.ValidationError(
                {"new_password": "Password must contain at least one uppercase letter."}
            )

        # At least one lowercase letter
        if not re.search(r"[a-z]", new_password):
            raise serializers.ValidationError(
                {"new_password": "Password must contain at least one lowercase letter."}
            )

        # At least one number
        if not re.search(r"[0-9]", new_password):
            raise serializers.ValidationError(
                {"new_password": "Password must contain at least one digit."}
            )

        # At least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            raise serializers.ValidationError(
                {
                    "new_password": "Password must contain at least one special character."
                }
            )
        return attrs
