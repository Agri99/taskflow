from rest_framework import serializers
from .models import AuditEntry


class AuditEntrySerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditEntry
        fields = ['id', 'actor', 'action', 'actor_username', 'target_content_type', 'timestamp', 'organization', 'payload',]
        read_only_fields = ['actor', 'actor_username', 'target_content_type', 'timestamp', 'organization', 'payload',]

    def get_actor_username(self, obj):
        return obj.actor.username if obj.actor else 'system'
