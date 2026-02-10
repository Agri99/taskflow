from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

from rbac.services import user_has_perm

class CommentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deletable_by(self, user):
        """Return comments deletable via RBAC or ownership (author only)."""
        if not user.is_authenticated:
            return self.none()
        
        # Authors can always delete their own comments
        own_comments = Q(author=user)

        # RBAC permission grants global delete ability
        if user_has_perm(user, 'comments.delete_comment'):
            return self.filter(deleted_at__isnull=True)
        
        return self.filter(own_comments, deleted_at__isnull=True)


    def editable_by(self, user):
        if not user or not user.is_authenticated:
            return self.none()
        
        cutoff = timezone.now() - timedelta(
            minutes=settings.COMMENTS_EDIT_WINDOW_MINUTES
        )
        
        return self.filter(
            author=user, 
            created_at__gt=cutoff, 
            deleted_at__isnull=True
            )
    
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