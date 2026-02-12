from django.db import models
from django.contrib.auth.models import User
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    

class MembershipProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='org_profile')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')