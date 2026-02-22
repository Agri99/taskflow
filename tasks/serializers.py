from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'status_display', 
                  'priority', 'priority_display', 'created_at', 'due_date']
        read_only_fields = ['id', 'created_at']

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_priority_display(self, obj):
        return obj.get_priority_display()