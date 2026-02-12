from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from tasks.models import Task
from comments.models import Comment
from rbac.models import AuditEntry, Membership, Role
from rbac.services_audit import audit_for_user, audit_for_object, audit_by_action

User = get_user_model()


class AuditServiceTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'Owner',
            password = 'pass1234'
        )
        self.author = User.objects.create_user(
            username = 'Auhtor',
            password = 'pass1234'
        )
        
        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = self.owner
        )

        self.comment = Comment.create_with_audit(
            task = self.task,
            author = self.owner,
            content = 'Hello'
        )

        # author edits comment (simulate audit event)
        AuditEntry.objects.create_entry(
            actor = self.author,
            action = AuditEntry.ACTION_EDIT,
            target = self.comment,
            payload = {'field':'content'}
        )

        ct = ContentType.objects.get_for_model(AuditEntry)
        perm = Permission.objects.get(
            content_type = ct,
            codename = 'view_auditentry'
        )

        role = Role.objects.create(
            name = 'Auditor',
            slug = 'auditor'
        )
        role.permissions.add(perm)

        Membership.objects.create(
            user = self.owner,
            role = role
        )

    def test_audit_for_user_returns_only_their_events(self):
        qs1 = audit_for_user(self.owner, requester=self.owner)
        qs2 = audit_for_user(self.author, requester=self.owner)

        self.assertEqual(qs1.count(), 1)
        self.assertEqual(qs2.count(), 1)

        self.assertEqual(qs1.first().actor, self.owner)
        self.assertEqual(qs2.first().actor, self.author)

    def test_audit_for_object_returns_events_for_that_object(self):
        qs = audit_for_object(self.comment, requester=self.owner)

        self.assertGreaterEqual(qs.count(), 1)
        for entry in qs:
            self.assertEqual(entry.target_object_id, self.comment.pk)

    def test_audit_by_action_filters_correctly(self):
        edit_logs = audit_by_action(AuditEntry.ACTION_EDIT, requester=self.owner)
        create_logs = audit_by_action(AuditEntry.ACTION_CREATE, requester=self.owner)

        self.assertTrue(all(e.action == AuditEntry.ACTION_EDIT for e in edit_logs))
        self.assertTrue(all(e.action == AuditEntry.ACTION_CREATE for e in create_logs))

    def test_audit_requires_permission(self):
        with self.assertRaises(PermissionDenied):
            audit_for_user(self.owner, requester=self.author)