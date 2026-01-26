from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class TaskDetailComments(TestCase):
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
            title = 'Task Test',
            description = 'Task Description',
            owner = self.owner
        )
        self.comment = Comment.objects.create(
            task = self.task,
            author = self.author,
            content = 'Task Comment'
        )

    def test_delete_comment_not_rendered_on_task_detail(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:task-detail',
            kwargs={'pk': self.task.pk}
            )

        # Delete comment attempt
        self.comment.soft_delete(by_user=self.author)

        self.comment.refresh_from_db()

        self.assertEqual(url.status_code, 200)
        self.assertNotContains(url, self.comment.content)