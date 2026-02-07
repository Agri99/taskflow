from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from comments.models import Comment
from tasks.models import Task
from rbac.models import Role, Membership
from rbac.services import get_user_permissions

User = get_user_model()


class PermissionResolutionTests(TestCase):
    def test_user_inherits_permissions_from_role(self):
        user = User.objects.create_user(
            username = 'permuser',
            password = 'x'
        )

        ct = ContentType.objects.get_for_model(Comment)
        perm = Permission.objects.get(content_type=ct, codename='delete_comment')

        role = Role.objects.create(
            name = 'Moderator',
            slug = 'moderator'
        )
        role.permissions.add(perm)

        Membership.objects.create(user=user, role=role)

        perms = get_user_permissions(user)

        self.assertIn('comments.delete_comment', perms)