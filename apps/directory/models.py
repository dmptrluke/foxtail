from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from .constants import COUNTRY_CHOICES, REGION_CHOICES
from .validators import URLValidator


class Profile(models.Model):
    url_validator = URLValidator()

    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)
    profile_URL = models.CharField(max_length=25, validators=[url_validator], blank=True, unique=True, null=True)

    country = models.CharField(max_length=20, blank=True, choices=COUNTRY_CHOICES)
    region = models.CharField(max_length=20, blank=True, choices=REGION_CHOICES)

    def __str__(self):
        return f"{self.profile_URL}"

    def get_absolute_url(self):
        return reverse('dir_profile', kwargs={'slug': self.profile_URL})

    def get_modify_url(self):
        return reverse('dir_profile_edit', kwargs={'slug': self.profile_URL})

    def can_modify(self, user: get_user_model()) -> bool:
        """
        Given a user, returns true if the user is allowed to edit this profile.
        """
        return user == self.user

    def clean(self):
        if self.country != 'NZ' and self.region:
            raise ValidationError({'region': 'Region may only be selected if country is New Zealand.'})


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
