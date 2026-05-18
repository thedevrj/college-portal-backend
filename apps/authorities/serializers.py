from rest_framework import serializers
from .models import Authority, AuthorityMember, AuthorityMinutes


class AuthorityMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorityMember
        fields = [
            "id",
            "authority",
            "provision",
            "name",
            "designation",
            "email",
            "phone_fax",
            "date_of_nomination",
            "date_of_expiry",
            "order",
        ]


class AuthorityMinutesSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = AuthorityMinutes
        fields = "__all__"

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None


class AuthoritySerializer(serializers.ModelSerializer):
    members = AuthorityMemberSerializer(many=True, read_only=True)
    minutes = AuthorityMinutesSerializer(many=True, read_only=True)

    class Meta:
        model = Authority
        fields = ["id", "name", "members", "minutes"]
