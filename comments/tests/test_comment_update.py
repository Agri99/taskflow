from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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