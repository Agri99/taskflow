from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from organizations.models import Organization, MembershipProfile
from rbac.models import Role, Membership
from tasks.models import Task
from comments.models import Comment

User = get_user_model()


class RBACIntegrationTest(TestCase):
    """Test that RBAC permissions actually work end-to-end"""
    def setUp(self):
        self.org = Organization.objects.create(name = 'Test Org')

        self.alice = User.objects.create_user(
            username = 'Alice',
            password = 'pass1234'
        )
        self.bob = User.objects.create_user(
            username = 'Bob',
            password = 'pass1234'
        )
        self.moderator = User.objects.create_user(
            username = 'moderator',
            password = 'pass1234'
        )

        for user in [self.alice, self.bob, self.moderator]:
            MembershipProfile.objects.create(
                user = user,
                organization = self.org,
                role = MembershipProfile.Role.MEMBER
            )

        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = self.alice,
            organization = self.org
        )

        self.comment = Comment.objects.create(
            task = self.task,
            author = self.bob,
            content = 'Bob comment',
            organization = self.org
        )

        ct = ContentType.objects.get_for_model(Comment)
        delete_perm = Permission.objects.get(content_type=ct, codename='delete_comment')

        self.moderator_role = Role.objects.create(name='Moderator', slug='moderator')
        self.moderator_role.permissions.add(delete_perm)

        Membership.objects.create(user=self.moderator, role=self.moderator_role)

    def test_moderator_can_delete_other_users_comment_via_rbac(self):
        client = Client()
        client.login(
            username = 'moderator',
            password = 'pass1234'
            )
        
        url = reverse(
            'tasks:comments:comment-delete',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            })
        
        response = client.post(url)

        self.assertEqual(response.status_code, 302)

        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)
        self.assertIsNotNone(self.comment.deleted_at)
        self.assertEqual(self.comment.deleted_by, self.moderator)

    def test_regular_user_cannot_delete_others_comment(self):
        stranger = User.objects.create_user(
            username = 'Stranger',
            password = 'pass1234'
        )
        MembershipProfile.objects.create(
            user = stranger,
            organization = self.org,
            role = MembershipProfile.Role.MEMBER
        )

        client = Client()
        client.login(
            username = 'Stranger',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-delete',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk
            }
        )

        response = client.post(url)

        self.assertEqual(response.status_code, 404)

        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_deleted)