from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class CommentDeletePermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'owner',
            password = 'pass1234'
        )
        self.author = User.objects.create_user(
            username = 'author',
            password = 'pass1234'
        )
        self.other_user = User.objects.create_user(
            username = 'other',
            password = 'pass1234'
        )
        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task description',
            owner = self.owner
        )

        self.comment = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Test Comment'
        )

    def test_comment_author_can_delete_comment(self):
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
    
    def test_task_owner_can_delete_others_comment(self):
        self.client.login(
            username = 'owner',
            password = 'pass1234'
        )

        url = reverse('tasks:comments:comment-delete',
                      kwargs={
                          'task_id': self.task.pk,
                          'pk': self.comment.pk,
                      })
        
        response = self.client.post(url)

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.is_deleted)
        self.assertIsNotNone(self.comment.deleted_at)
        
    def test_random_user_cannot_delete_comment(self):
        self.client.login(
            username = 'other',
            password = 'pass1234'
        )
        url = reverse('tasks:comments:comment-delete',
                      kwargs={
                          'task_id': self.task.pk,
                          'pk': self.comment.pk,
                      })
        
        response = self.client.post(url)

        self.comment.refresh_from_db

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.comment.is_deleted)

    def test_wrong_task_id_returns_404(self):
        self.client.login(
            username = 'author',
            password = 'pass1234',
        )

        wrong_task_id = self.task.pk + 999

        url = reverse('tasks:comments:comment-delete',
                      kwargs={
                          'task_id': wrong_task_id,
                          'pk': self.comment.pk,
                      })
        
        response = self.client.post(url)

        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.comment.is_deleted)