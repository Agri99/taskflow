from django.test import TestCase
from django.contrib.auth import get_user_model

from organizations.models import Organization
from tasks.models import Task
from comments.models import Comment

User = get_user_model()


class CommentIsolationTests(TestCase):
    def setUp(self):
        self.orgA = Organization.objects.create(name='Org A')
        self.orgB = Organization.objects.create(name='Org B')

        self.userA = User.objects.create_user(
            username = 'User A',
            password = 'pass1234'
        )
        self.userB = User.objects.create_user(
            username = 'User B',
            password = 'pass1234'
        )

        self.userA.organization = self.orgA
        self.userA.save()

        self.userB.organization = self.orgB
        self.userB.save()

        self.task = Task.objects.create(
            title = 'Secret Task',
            owner = self.userB,
            organization = self.orgB
        )

        self.comment = Comment.objects.create(
            task = self.task,
            author = self.userB,
            content = 'Secret Comment',
            organization = self.orgB
        )

    def test_user_cannot_see_other_org_comment(self):
        qs = Comment.objects.for_user(self.userA)

        self.assertNotIn(self.comment, qs)

    def test_queryset_filter_blocks_direct_access(self):
        qs = Comment.objects.for_user(self.userA)

        exists = qs.filter(pk=self.comment.pk).exists()

        self.assertFalse(exists)