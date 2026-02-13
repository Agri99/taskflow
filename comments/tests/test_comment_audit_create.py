from django.test import TestCase
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment
from rbac.models import AuditEntry
from organizations.models import Organization, MembershipProfile

User = get_user_model()


class CommentCreateAuditTests(TestCase):
    def test_creating_comment_creates_audit_entry(self):
        user = User.objects.create_user(
            username = 'Owner',
            password = 'pass1234'
        )

        organization = Organization.objects.create(
            name = 'Test Org'
        )
        MembershipProfile.objects.create(
            user = user,
            organization = organization,
        )

        task = Task.objects.create(
            title = 'Task Test',
            description = 'Task Description',
            owner = user,
            organization = organization
        )

        comment = Comment.create_with_audit(
            task = task,
            author = user,
            content = "Hello World!"
        )

        log = AuditEntry.objects.get(
            action = AuditEntry.ACTION_CREATE,
            target_object_id = comment.id,
        )

        self.assertEqual(log.actor, user)
        self.assertEqual(log.payload['content'], "Hello World!")
        self.assertEqual(log.payload['author_id'], user.id)
        self.assertEqual(log.payload['task_id'], task.id)