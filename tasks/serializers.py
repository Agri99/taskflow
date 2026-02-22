from rest_framework import serializers
from .models import Task


class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'created_at', 'due_date']
        read_only_fields = ['id', 'created_at']