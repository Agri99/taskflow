from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

User = get_user_model()

class CommentUIVisibilityTest(TestCase):
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
            content = 'Editable comment',
            created_at = timezone.now()
        )

    def test_author_sees_edit_button_within_edit_window(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:task-detail',
            kwargs={
                'pk': self.task.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        edit_url = reverse(
            'tasks:comments:comment-edit',
            kwargs={
                'task_id': self.task.pk,
                'pk': self.comment.pk
            }
        )

        self.assertContains(response, edit_url)

    def test_new_comment_does_not_show_badge(self):
        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:task-detail',
            kwargs={
                'pk': self.task.pk
            }
        )

        response = self.client.get(url)

        self.assertNotContains(response, '(edited)')

    def test_edited_comment_show_badge(self):
        # Simulate and edit
        self.comment.content = 'Edited content'
        self.comment.edited_at = timezone.now()
        self.comment.save()

        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:task-detail',
            kwargs={
                'pk': self.task.pk
            }
        )

        response = self.client.get(url)

        self.assertContains(response, '(edited)')

    def test_deleted_comment_doest_not_show_edited_badge(self):
        self.comment.edited_at = timezone.now()
        self.comment.is_deleted = True
        self.comment.deleted_at = timezone.now()
        self.comment.save()

        self.client.login(
            username = 'author',
            password = 'pass1234'
        )

        url = reverse(
            'tasks:task-detail',
            kwargs={
                'pk': self.task.pk
            }
        )

        response = self.client.get(url)

        self.assertNotContains(response, '(edited)')