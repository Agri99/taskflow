from django.core.management.base import BaseCommand
from comments.models import Comment
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Purge soft-deleted comments older than given days'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(days=days)
        qs = Comment.all_objects.purge_older_than(days)
        count = qs.count()
        self.stdout.write(f'Found {count} comments to purge.')
        if dry_run:
            return
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f'Purged {count} comments'))