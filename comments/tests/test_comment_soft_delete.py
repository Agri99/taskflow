from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class CommentSoftDelete(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        self.author = User.objects.create_user(
            username = 'author',
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
            content = 'Test Comment'
        )

    def test_soft_delete_marks_comment_deleted(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-delete',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk,
            }
        )

        response = self.client.post(url)

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.is_deleted)
        self.assertIsNotNone(self.comment.deleted_at)
        self.assertEqual(self.comment.deleted_by, self.author)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

        comment = Comment.all_objects.get(pk=self.comment.pk)
        
        self.assertTrue(comment.is_deleted)
        self.assertIsNotNone(comment.deleted_at)
        self.assertTrue(Comment.all_objects.filter(pk=self.comment.pk).exists())

    def test_deleting_already_deleted_comment_is_idempotent(self):
        # First delete
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:comments:comment-delete',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk
            }
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302) # initial delete redirect

        self.comment.refresh_from_db()
        original_deleted_at = self.comment.deleted_at
        self.assertIsNotNone(original_deleted_at)

        # Second delete attempt
        response = self.client.post(url)
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.comment.deleted_at, original_deleted_at)
        