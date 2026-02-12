from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from tasks.models import Task
from comments.models import Comment
from rbac.models import AuditEntry, Membership, Role
from rbac.services_audit import audit_for_user, audit_for_object, audit_by_action
from organizations.models import Organization, MembershipProfile

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

        self.orgA = Organization.objects.create(
            name = 'Organization A'
        )
        self.orgB = Organization.objects.create(
            name = 'Organization B'
        )
        MembershipProfile.objects.create(
            user = self.owner,
            organization = self.orgA
        )
        MembershipProfile.objects.create(
            user = self.author,
            organization = self.orgB
        )
        
        self.taskA = Task.objects.create(
            title = 'Test Task A',
            description = 'Task Description',
            owner = self.owner,
            organization = self.orgA
        )
        self.taskB = Task.objects.create(
            title = 'Test Task B',
            description = 'Task Description',
            owner = self.owner,
            organization = self.orgB
        )

        self.commentA = Comment.create_with_audit(
            task = self.taskA,
            author = self.owner,
            content = 'Hello A'
        )
        self.commentB = Comment.create_with_audit(
            task = self.taskB,
            author = self.author,
            content = 'Hello B'
        )

        # author edits comment (simulate audit event)
        AuditEntry.objects.create_entry(
            actor = self.owner,
            action = AuditEntry.ACTION_EDIT,
            target = self.commentA,
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

        for entry in qs1:
            self.assertEqual(entry.organization, self.orgA)
        for entry in qs2:
            self.assertEqual(entry.organization, self.orgB)

    def test_audit_for_object_returns_events_for_that_object(self):
        qs = audit_for_object(self.commentA, requester=self.owner)

        for entry in qs:
            self.assertEqual(entry.target_object_id, self.commentA.pk)

    def test_audit_by_action_filters_correctly(self):
        edit_logs = audit_by_action(AuditEntry.ACTION_EDIT, requester=self.owner)
        create_logs = audit_by_action(AuditEntry.ACTION_CREATE, requester=self.owner)

        self.assertTrue(all(e.action == AuditEntry.ACTION_EDIT for e in edit_logs))
        self.assertTrue(all(e.action == AuditEntry.ACTION_CREATE for e in create_logs))

    def test_audit_requires_permission(self):
        with self.assertRaises(PermissionDenied):
            audit_for_user(self.owner, requester=self.author)

    def test_owner_cannot_see_other_organization_logs(self):
        logs = audit_by_action(AuditEntry.ACTION_CREATE, requester=self.owner)

        for entry in logs:
            self.assertEqual(entry.organization, self.orgA)