from celery import shared_task
from .models import Comment

@shared_task
def purge_old_comments(days=30):
    qs = Comment.all_objects.purge_older_than(days)
    deleted_count = qs.count()
    qs.delete()
    return f'Purged {deleted_count} comments'