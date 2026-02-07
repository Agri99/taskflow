from django.test import TestCase
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

User = get_user_model()


class AuditOnCommentDeleteTest(TestCase):
    def test_audit_entry_created_on_soft_delete(self):
        """When a comment is soft-deleted, an AuditEntry with action='delete'"""
        user = User.objects.create_user(
            username = 'audittest',
            password = 'password'
        )
        task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = user
        )
        comment = Comment.objects.create(
            task = task,
            author = user,
            content = 'Hello'
        )

        # perform soft-delete
        comment.soft_delete(by_user = user)

        # lazy import to avoid cross-import issues during test discovery
        from rbac.models import AuditEntry

        assert AuditEntry.objects.filter(
            action = AuditEntry.ACTION_DELETE,
            actor = user,
            target_object_id = comment.pk,
        ).exists()