from django.db import models


# Create your models here.
from apps.users.models import User


class Character(models.Model):
    name = models.CharField(max_length=100, help_text="100 characters or fewer.")
    species = models.CharField(max_length=100, help_text="100 characters or fewer.")
    gender = models.CharField(max_length=100, default='', blank=True, help_text="100 characters or fewer.")
    description = models.TextField(blank=True, default='')

    user = models.ForeignKey(User, on_delete=models.CASCADE)


__all__ = ['Character']
