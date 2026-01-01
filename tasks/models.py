from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    STATUS_CHOICES = [
        ('T', 'todo'),
        ('I', 'in_progress'),
        ('D', 'done'),
    ]
    PRIORITY_CHOICES = [
        ('L', 'low'),
        ('M', 'medium'),
        ('H', 'high'),
    ]
    title = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='T')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='L')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title