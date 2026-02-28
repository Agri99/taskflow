from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    is_edited = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'content', 'created_at', 'edited_at', 'is_edited']
        read_only_fields = ['id', 'author', 'created_at', 'edited_at', 'is_edited']

    def get_author_username(self, obj):
        return obj.author.username
    
    def get_is_edited(self, obj):
        return obj.is_edited