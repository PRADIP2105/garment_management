from rest_framework import serializers

from apps.workers.models import Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            "id",
            "name",
            "mobile_number",
            "address",
            "city",
            "skill_type",
            "machine_type",
            "status",
            "language_preference",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

