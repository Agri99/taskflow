from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from django.contrib.auth import get_user_model

from comments.models import Comment
from tasks.models import Task

User = get_user_model()

class CommentPurgeTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        self.author = User.objects.create_user(
            username = 'author',
            password = 'pass1234'
        )
        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task description',
            owner = self.owner
        )

        # Create two deleted comments
        self.old = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Old comment'
        )
        self.old.is_deleted = True
        self.old.deleted_at = timezone.now() - timedelta(days=31)
        self.old.save(update_fields=['is_deleted', 'deleted_at'])

        self.recent = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Recent comment'
        )
        self.recent.is_deleted = True
        self.recent.deleted_at = timezone.now() - timedelta(days=10)
        self.recent.save(update_fields=['is_deleted', 'deleted_at'])

    def test_purge_removes_only_old_deleted_comments(self):
        call_command('purge_deleted_comments', '--days', 30)
        self.assertFalse(Comment.all_objects.filter(pk=self.old.pk).exists())
        self.assertTrue(Comment.all_objects.filter(pk=self.recent.pk).exists())
        
    def test_purge_dry_run_does_not_delete(self):
        call_command('purge_deleted_comments', '--days', '30', '--dry-run')
        self.assertTrue(Comment.all_objects.filter(pk=self.old.pk).exists())
        self.assertTrue(Comment.all_objects.filter(pk=self.recent.pk).exists())

    def test_purge_does_not_touch_active_comments(self):
        active = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Active comment'
        )
        call_command('purge_deleted_comments', '--days', '0')
        self.assertTrue(Comment.all_objects.filter(pk=active.pk).exists())