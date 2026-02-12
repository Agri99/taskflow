import pytest
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from tasks.models import Task
from comments.models import Comment

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

    task = Task.objects.create(
        title = 'Test Task',
        description = 'Task Description',
        owner = owner
    )

    comment = Comment.objects.create(
        task = task,
        author = owner,
        content = 'Hello'
    )

    with pytest.raises(PermissionDenied):
        comment.soft_delete(by_user=other)