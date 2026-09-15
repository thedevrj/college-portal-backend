from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
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

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return attrs
