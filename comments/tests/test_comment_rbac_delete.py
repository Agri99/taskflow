from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from tasks.models import Task
from comments.models import Comment
from rbac.models import Role, Membership

User = get_user_model()


class CommentRBACDeleteTests(TestCase):
    def test_user_with_delete_permission_can_delete_other_comment(self):
        owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        moderator = User.objects.create_user(
            username = 'mod',
            password = 'pass1234'
        )
        task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = owner
        )
        comment = Comment.objects.create(
            task = task,
            author = owner,
            content = 'Comment body'
        )

        # Create permission
        ct = ContentType.objects.get_for_model(Comment)
        perm = Permission.objects.get(
            content_type = ct,
            codename = 'delete_comment'
            )
        
        # Create role and assign permission
        role = Role.objects.create(
            name = 'Moderator',
            slug = 'moderator'
        )
        role.permissions.add(perm)

        # Assign role to moderator
        Membership.objects.create(
            user = moderator,
            role = role
        )

        # Moderator is NOT the author - but should still be allowed

        assert comment.can_be_deleted_by(moderator) is True

    def test_user_without_permission_cannot_delete_others_comment(self):
        owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        stranger = User.objects.create_user(
            username = 'stranger',
            password = 'pass 1234'
        )
        task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = owner
        )
        comment = Comment.objects.create(
            task = task,
            author = owner,
            content = 'Comment body'
        )

        assert comment.can_be_deleted_by(stranger) is False