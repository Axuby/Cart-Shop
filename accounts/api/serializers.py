from accounts.models import Account, UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"

    def validate(self, obj):
        request = self.context.get("request")
        if request.user != obj.get("user"):
            raise serializers.ValidationError(
                "Your are not allowed to view this profile")
        return obj


class AccountSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source="userprofile")

    class Meta:
        model = Account
        fields = ("id", "username", "first_name",
                  "last_name", "email", "profile")
