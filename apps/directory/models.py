from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
from apps.accounts.models import User


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    description = models.TextField(blank=True, default='')
    gender = models.CharField(
        max_length=100, default='', blank=True, help_text="100 characters or fewer."
    )

    class Meta:
        permissions = (('directory_view', 'Can View Profile'),)


class Character(models.Model):
    name = models.CharField(max_length=100, help_text="100 characters or fewer.")
    species = models.CharField(max_length=100, help_text="100 characters or fewer.")
    gender = models.CharField(
        max_length=100, default='', blank=True, help_text="100 characters or fewer."
    )
    description = models.TextField(blank=True, default='')

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


__all__ = ['Profile', 'Character']
