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