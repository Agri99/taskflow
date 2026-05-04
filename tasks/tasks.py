from celery import shared_task
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType

from organizations.models import MembershipProfile
from .models import Task
from rbac.models import AuditEntry


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_org_members_new_task(self, task_id):
    try:
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

        # Mark notification as sent
        task.notification_sent = True
        task.save()

        # Log success to audit (actor=None, system action)
        AuditEntry.objects.create(
            actor=None,
            action='notification',
            target_content_type=ContentType.objects.get_for_model(Task),
            target_object_id=task.id,
            payload={'status': 'completed'},
            organization=task.organization
        )
    
    except Exception as exc:
        # Log success to audit (actor=None, system action)
        AuditEntry.objects.create(
            actor=None,
            action='notification',
            target_content_type=ContentType.objects.get_for_model(Task),
            target_object_id=task.id,
            payload={'status': 'failed', 'error': str(exc)},
            organization=task.organization
        )
        raise self.retry(exc=exc)
        