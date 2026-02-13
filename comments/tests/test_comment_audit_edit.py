from django.test import TestCase
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment
from rbac.models import AuditEntry
from organizations.models import Organization, MembershipProfile

User = get_user_model()


class CommentAuditEditTest(TestCase):
    def test_audit_entry_created_with_diff_on_edit(self):
        user = User.objects.create_user(
            username = 'Editor',
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
        comment = Comment.objects.create(
            task = task,
            author = user,
            content = 'Hello!'
        )
        comment.apply_edit(
            new_content = 'Hello World!',
            by_user = user
            )
        
        audit = AuditEntry.objects.get(action=AuditEntry.ACTION_EDIT)

        assert audit.actor == user
        assert audit.payload['content']['old'] == 'Hello!'
        assert audit.payload['content']['new'] == 'Hello World!'

    def test_creating_comment_creates_audit_entry(self):
        user = User.objects.create_user(
            username = 'editor',
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
        comment = Comment.objects.create(
            task = task,
            author = user,
            content = 'Old text'
        )

        comment.edit_with_audit(
            new_content = 'Updated text!',
            by_user = user
            )
        
        log = AuditEntry.objects.get(
            action = AuditEntry.ACTION_EDIT,
            target_object_id = comment.id
        )

        self.assertEqual(log.actor, user)
        self.assertEqual(log.payload['old_content'], 'Old text')
        self.assertEqual(log.payload['new_content'], 'Updated text!')