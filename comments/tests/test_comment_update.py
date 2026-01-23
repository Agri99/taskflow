from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class CommentUpdatePermissionTests(TestCase):
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
            title = 'Task',
            description = 'Test Description',
            owner = self.owner
        )

        self.comment = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Original'
        )

    def test_author_can_edit_comment(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
            )
        
        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'Updated'})

        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated')

    def test_task_owner_cannot_edit_comment(self):
        self.client.login(
            username = 'owner',
            password = 'pass1234',
        )
        
        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'Hacked'})

        self.assertEqual(response.status_code, 404)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original')

    def test_random_user_cannot_edit_comment(self):
        self.client.login(
            username = 'other',
            password = 'pass1234',
        )

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'Nope'})

        self.assertEqual(response.status_code, 404)

    def test_author_cannot_edit_comment_after_edit_window(self):
        # Move comment outside edit window
        self.comment.created_at = timezone.now() - timedelta(
            minutes=settings.COMMENTS_EDIT_WINDOW_MINUTES + 1)
        self.comment.save(update_fields=['created_at'])

        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'Too late'})

        self.comment.refresh_from_db()

        self.assertNotEqual(self.comment.content, 'Too late')
        self.assertEqual(response.status_code, 404)

    def test_author_cannot_edit_comment_exactly_at_edit_window_boundary(self):
        '''
        Editing should be forbiddem exactly at the edit window cutoff
        '''
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        now = timezone.now()

        boundary_time = now - timedelta(
            minutes=settings.COMMENTS_EDIT_WINDOW_MINUTES
        )

        Comment.objects.filter(pk=self.comment.pk).update(created_at=boundary_time)

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )
        
        response = self.client.post(url, {'content': 'Too late'})

        self.assertEqual(response.status_code, 404)

    def test_author_cannot_edit_deleted_comment_even_within_edit_window(self):
        '''
        Editing a soft-deleted comment should always forbidden
        '''
        # Soft delete the comment
        self.comment.is_deleted = True
        self.comment.deleted_at = timezone.now()
        self.comment.save(update_fields=['is_deleted', 'deleted_at'])

        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'Should not work'})

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(self.comment.content, 'Should not work')

    def test_random_user_cannot_load_edit_form(self):
        self.client.login(
            username = 'other',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk
            }
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_first_edit_sets_edited_at(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url, {'content': 'edited'})

        self.comment.refresh_from_db()
        self.assertIsNotNone(self.comment.edited_at)

    def test_second_edit_does_not_change_edited_at(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
        'tasks:comments:comment-edit',
        kwargs={
            'task_id': self.task.pk,
            'pk': self.comment.pk,
            }
        )

        # First edit attempt
        self.client.post(url, {'content': 'edited once'})
        first_time = Comment.objects.get(pk=self.comment.pk).edited_at

        self.client.post(url, {'content': 'edited twice'})
        self.comment.refresh_from_db()

        self.assertEqual(self.comment.edited_at, first_time)

    def test_new_comment_is_not_edited(self):
        self.assertFalse(self.comment.is_edited)
        self.assertIsNone(self.comment.edited_at)

    def test_editing_comment_sets_edited_flag(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )
        
        url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk
            }
        )

        self.client.post(url, {'content': 'Edited comment'})

        self.comment.refresh_from_db()

        self.assertTrue(self.comment.is_edited)
        self.assertIsNotNone(self.comment.edited_at)

    def test_edited_at_is_not_overwritten_on_second_attempt(self):
        first_edit_time = timezone.now() - timedelta(minutes=5)

        self.comment.edited_at = first_edit_time
        self.comment.save(update_fields=['edited_at'])

        self.comment.mark_edited()
        self.comment.save()

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.edited_at, first_edit_time)