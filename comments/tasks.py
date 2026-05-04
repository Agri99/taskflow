from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Comment
from rbac.models import AuditEntry
from organizations.models import Organization

User = get_user_model()


@shared_task
def purge_old_comments(days=30):
    from organizations.models import Organization

    for org in Organization.objects.all():
        qs = Comment.all_objects.filter(organization=org).purge_older_than(days)
        deleted_count = qs.count()
        qs.delete()

        if deleted_count > 0:
            # Log the purge action
            AuditEntry.objects.create(
                actor=None,
                action='delete',
                target_content_type=ContentType.objects.get_for_model(Comment),
                target_object_id=None, # No single object
                payload={'deleted_count': deleted_count, 'older_than_days': days},
                organization=org, # System-wide action, no org
            )

    return f'Purged {deleted_count} comments'

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_audit_entry(self, actor_id, action, target_content_type_id, target_object_id, payload, organization_id):
    try:
        actor = User.objects.get(pk=actor_id) if actor_id else None
        organization = Organization.objects.get(pk=organization_id)
        ct = ContentType.objects.get(pk=target_content_type_id)

        AuditEntry.objects.get_or_create(
            actor=actor,
            action=action,
            target_content_type=ct,
            target_object_id=target_object_id,
            payload=payload,
            organization=organization
        )
    except Exception as exc:
        raise self.retry(exc=exc)
