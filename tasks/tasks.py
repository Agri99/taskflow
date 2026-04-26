from celery import shared_task
from django.core.mail import send_mail

from organizations.models import MembershipProfile
from .models import Task


@shared_task
def notify_org_members_new_task(task_id):
    task = Task.objects.get(id=task_id)
    member_emails = MembershipProfile.objects.filter(
        organization=task.organization
    ).values_list('user__email', flat=True)
    for email in member_emails:
        send_mail(
            'New Task Created',
            f'A new task "{task.title}" has been created. Please have a look!',
            'noreply@taskflow.com',
            [email]
        )