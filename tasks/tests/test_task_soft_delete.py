import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from tasks.models import Task
from organizations.models import Organization, MembershipProfile

User = get_user_model()


class TaskSoftDelete(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username = 'Owner',
            password = 'pass1234'
        )
        self.other = User.objects.create_user(
            username = 'Other',
            password = 'pass1234'
        )

        self.organization = Organization.objects.create(
            name = 'Test Org'
        )
        MembershipProfile.objects.create(
            user = self.owner,
            organization = self.organization
        )
        MembershipProfile.objects.create(
            user = self.other,
            organization = self.organization
        )

        self.task = Task.objects.create(
            title = 'Test Task',
            description = 'Task Desc',
            owner = self.owner,
            organization = self.organization
        )

    def test_owner_can_soft_delete_their_task(self):
        self.task.soft_delete(by_user=self.owner)

        self.task.refresh_from_db()

        self.assertTrue(self.task.is_deleted)
        self.assertIsNotNone(self.task.deleted_at)
        self.assertFalse(Task.objects.active().filter(pk=self.task.pk).exists())

    def test_non_owner_cannot_soft_delete(self):
        with pytest.raises(PermissionDenied):
            self.task.soft_delete(by_user=self.other)

        self.task.refresh_from_db()

        self.assertFalse(self.task.is_deleted)
        self.assertIsNone(self.task.deleted_at)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())
