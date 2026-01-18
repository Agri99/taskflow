from django.core.management.base import BaseCommand
from comments.models import Comment

class Command(BaseCommand):
    help = 'Permanently delete comments soft-deleted more than 30 days ago'

    def handle(self, *args, **options):
        qs = Comment.objects.purge_older_than(days=30)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Purged {count} comments'))