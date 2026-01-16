from django.db import models
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def can_be_deleted_by(self, user):
        return user == self.author or user == self.task.owner

    def __str__(self):
        return f'Comment by {self.author}'