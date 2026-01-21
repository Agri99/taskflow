from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class CommentQuerysetTests(TestCase):
    
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        self.author = User.objects.create_user(
            username = 'author',
            password = 'pass1234'
        )
        self.other = User.objects.create_user(
            username = 'other',
            password = 'pass1234'
        )
        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Description',
            owner = self.owner
        )
        self.comment = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Task Comment'
        )

    def test_deleted_comment_is_excluded_from_editable_queryset_even_within_edit_window(self):
        # Sanity: Comment is within edit window
        self.comment.created_at = timezone.now()
        self.comment.save(update_fields=['created_at'])

        # Soft delete the comment
        self.comment.is_deleted = True
        self.comment.deleted_at = timezone.now()
        self.comment.save(update_fields=['is_deleted', 'deleted_at'])

        qs = Comment.objects.editable_by(self.author)

        self.assertNotIn(self.comment, qs)

    def test_deleted_comment_excluded_from_deletable_by_author(self):
        # Soft delete comment
        self.comment.is_deleted = True
        self.comment.deleted_at = timezone.now()
        self.comment.save(update_fields=['is_deleted', 'deleted_at'])

        qs = Comment.objects.deletable_by(self.author)
        self.assertNotIn(self.comment, qs)
    
    def test_deleted_comment_excluded_from_deletable_by_owner(self):
        # Soft delete comment
        self.comment.is_deleted = True
        self.comment.deleted_at = timezone.now()
        self.comment.save(update_fields=['is_deleted', 'deleted_at'])

        qs = Comment.objects.deletable_by(self.owner)
        self.assertNotIn(self.comment, qs)