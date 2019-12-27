from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import REGION_CHOICES
from .validators import URLValidator


class Profile(models.Model):
    url_validator = URLValidator()

    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)
    profile_URL = models.CharField(max_length=25, validators=[url_validator], blank=True, unique=True, null=True)

    region = models.CharField(max_length=20, blank=True, choices=REGION_CHOICES)

    def __str__(self):
        return f"{self.user.username}"

    def get_absolute_url(self):
        return reverse('dir_profile', kwargs={'slug': self.profile_URL})

    def get_modify_url(self):
        return reverse('dir_profile_edit', kwargs={'pk': self.pk})


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
