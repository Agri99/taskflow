import pytest
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment
from organizations.models import Organization, MembershipProfile

User = get_user_model()


@pytest.mark.django_db
def test_soft_delete_blocked_without_permission():
    owner = User.objects.create_user(
        username = 'Owner',
        password = 'pass1234'
    )
    other = User.objects.create_user(
        username = 'Other',
        password = 'pass1234'
    )

    organization = Organization.objects.create(
        name = 'Test Org'
    )
    MembershipProfile.objects.create(
        user = owner,
        organization = organization,
    )
        
    task = Task.objects.create(
        title = 'Task Test',
        description = 'Task Description',
        owner = owner,
        organization = organization
    )

    comment = Comment.objects.create(
        task = task,
        author = owner,
        content = 'Hello'
    )

    with pytest.raises(PermissionDenied):
        comment.soft_delete(by_user=other)