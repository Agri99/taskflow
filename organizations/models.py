from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

class MembershipProfile(models.Model):
    """This model stores the user's organization membership and role."""
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='org_profile',
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
    )
    
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default = Role.MEMBER,
        )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"