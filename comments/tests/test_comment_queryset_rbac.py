from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from tasks.models import Task
from comments.models import Comment
from rbac.models import Role, Membership

User = get_user_model()


class CommentQuerysetRBACTests(TestCase):
    def test_query_only_returned_owned_comments_without_permission(self):
        owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        other = User.objects.create_user(
            username = 'other',
            password = 'pass1234'
        )
        task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = owner
        )

        c1 = Comment.objects.create(
            task = task,
            author = owner,
            content = 'Mine'
        )
        c2 = Comment.objects.create(
            task = task,
            author = other,
            content = 'Not mine'
        )

        qs = Comment.objects.deletable_by(owner)

        assert c1 in qs
        assert c2 not in qs

    def test_queryset_returns_all_comments_for_user_with_permission(self):
        owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        moderator = User.objects.create_user(
            username = 'Moderator',
            password = 'pass1234'
        )
        task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = owner
        )

        c1 = Comment.objects.create(
            task = task,
            author = owner,
            content = 'First'
        )
        c2 = Comment.objects.create(
            task = task,
            author = moderator,
            content = 'Second'
        )

        ct = ContentType.objects.get_for_model(Comment)
        perm = Permission.objects.get(
            content_type = ct,
            codename = 'delete_comment'
            )
        
        role = Role.objects.create(
            name = 'Moderator2',
            slug = 'moderator2'
        )
        role.permissions.add(perm)
        Membership.objects.create(
            user = moderator,
            role = role
            )

        qs = Comment.objects.deletable_by(moderator)

        assert c1 in qs
        assert c2 in qs