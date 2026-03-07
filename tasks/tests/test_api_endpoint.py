from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


from organizations.models import Organization, MembershipProfile
from tasks.models import Task
from comments.models import Comment

User = get_user_model()


class APITest(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            username = 'Moderator',
            password = 'pass1234'
        )

        self.org = Organization.objects.create(name='Org')

        MembershipProfile.objects.create(
            user = self.moderator,
            organization = self.org,
            role = MembershipProfile.Role.ADMIN
        )

        refresh = RefreshToken.for_user(self.moderator)
        token = str(refresh.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        self.task = Task.objects.create(
            title = 'Task Test',
            description = 'Task Desc',
            owner = self.moderator,
            organization = self.org
        )

        self.comment = Comment.objects.create(
            task = self.task,
            author = self.moderator,
            content = 'Moderator comment',
            organization = self.org
        )

    def test_authenticated_user_can_list_tasks(self):
        url = reverse('tasks-api:task-api-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)