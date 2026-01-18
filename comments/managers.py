from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class CommentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deletable_by(self, user):
        if not user or not user.is_authenticated:
            return self.none()
        
        return self.filter(
            Q(author=user) | Q(task__owner=user) # Q is used to express the OR cleanly
        )
    
    def editable_by(self, user):
        if not user or not user.is_authenticated:
            return self.none()
        
        return self.filter(author=user)
    
    def purge_older_than(self, days):
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(
            is_deleted=True, deleted_at__lt=cutoff
        )
    
class CommentManager(models.Manager):
    def get_queryset(self):
        # Default: return only active comments.
        qs = CommentQuerySet(self.model, using=self._db)
        # Toggle behavior by setting.COMMENTS_ACTIVE_ONLY
        return qs.active() if getattr(settings, 'COMMENTS_ACTIVE_ONLY', True) else qs
    
    def deletable_by(self, user):
        return self.get_queryset().deletable_by(user)
    
    def editable_by(self, user):
        return self.get_queryset().editable_by(user)
    
    def with_deleted(self):
        # Return a QuerySet that includes deleted comments
        return CommentQuerySet(self.model, using=self._db)