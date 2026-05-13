from rest_framework import serializers
from .models import Authority, AuthorityMember, AuthorityMinutes

class AuthorityMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorityMember
        fields = "__all__"

class AuthorityMinutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorityMinutes
        fields = "__all__"

class AuthoritySerializer(serializers.ModelSerializer):
    members = AuthorityMemberSerializer(many=True, read_only=True)
    minutes = AuthorityMinutesSerializer(many=True, read_only=True)

    class Meta:
        model = Authority
        fields = ["id", "name", "description", "members", "minutes"]
