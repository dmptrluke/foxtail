from django.contrib.auth import get_user_model
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}"


class Character(models.Model):
    name = models.CharField(max_length=100, help_text="100 characters or fewer.")
    species = models.CharField(max_length=100, help_text="100 characters or fewer.")
    gender = models.CharField(
        max_length=100, default='', blank=True, help_text="100 characters or fewer."
    )
    description = models.TextField(blank=True, default='')

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='characters')

    def __str__(self):
        return f"{self.name} {self.user.username}"


__all__ = ['Profile', 'Character']
