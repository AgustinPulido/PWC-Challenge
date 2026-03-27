from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["customer_id", "name", "email", "country", "age", "created_at", "updated_at"]
        read_only_fields = ["customer_id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()

    def validate_age(self, value: int | None) -> int | None:
        if value is not None and value < 18:
            raise serializers.ValidationError("Age must be greater than or equal to 18")
        return value

