from rest_framework import serializers
from .models import MOU


class MOUSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOU
        fields = "__all__"

    def validate(self, attrs):
        organization_name = attrs.get("organization_name")
        date_of_signing = attrs.get("date_of_signing")

        if organization_name and date_of_signing:
            qs = MOU.objects.filter(
                organization_name__iexact=organization_name,
                date_of_signing=date_of_signing,
                is_deleted=False,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "An MOU with the same Partner Name and Date of Signing already exists."
                )
        return attrs
