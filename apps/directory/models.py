from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from .constants import COUNTRY_CHOICES, REGION_CHOICES
from .validators import validate_blacklist, validate_url


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)
    profile_URL = models.CharField(max_length=25, validators=[validate_url, validate_blacklist],
                                   unique=True)

    country = models.CharField(max_length=20, blank=True, choices=COUNTRY_CHOICES)
    region = models.CharField(max_length=20, blank=True, choices=REGION_CHOICES)

    def __str__(self):
        return f"{self.profile_URL}"

    def get_absolute_url(self):
        return reverse('directory:profile', kwargs={'slug': self.profile_URL})

    def get_modify_url(self):
        return reverse('directory:profile_edit', kwargs={'slug': self.profile_URL})

    def can_modify(self, user: get_user_model()) -> bool:
        """
        Given a user, returns true if the user is allowed to edit this profile.
        """
        return True

    def clean(self):
        if self.country != 'NZ' and self.region:
            raise ValidationError({'region': 'Region may only be selected if country is New Zealand.'})

        if self.country != 'NZ' and self.region:
            raise ValidationError({'region': 'Region may only be selected if country is New Zealand.'})

    @property
    def location(self):
        if not self.country:
            return " - "

        if self.country == 'NZ':
            loc = self.get_region_display()
        else:
            loc = self.get_country_display()

        flag = static(f'flags/{self.country.lower()}.png')
        return mark_safe(f'<img src="{flag}" /> {loc}')

    @cached_property
    def structured_data(self):
        return {
            '@type': 'Person',
            '@id': 'https://furry.nz/' + self.get_absolute_url(),
            'name': self.user
        }


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
