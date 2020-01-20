from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html

from ..constants import COUNTRY_CHOICES, REGION_CHOICES
from ..fields import PrivacyField
from ..validators import validate_blacklist, validate_url
from .base import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(get_user_model(), primary_key=True, on_delete=models.CASCADE)
    profile_URL = models.CharField(max_length=25, validators=[validate_url, validate_blacklist],
                                   unique=True)

    description = models.TextField(blank=True)
    description_privacy = PrivacyField()

    country = models.CharField(max_length=20, blank=True, choices=COUNTRY_CHOICES)
    region = models.SmallIntegerField(blank=True, null=True, choices=REGION_CHOICES)
    location_privacy = PrivacyField()

    def __str__(self):
        return f"{self.profile_URL}"

    def get_absolute_url(self):
        return reverse('directory:profile', kwargs={'slug': self.profile_URL})

    def get_modify_url(self):
        return reverse('directory:profile_edit', kwargs={'slug': self.profile_URL})

    def clean(self):
        if self.country != 'NZ' and self.region:
            raise ValidationError({'region': 'Region may only be selected if country is New Zealand.'})

        if self.country != 'NZ' and self.region:
            raise ValidationError({'region': 'Region may only be selected if country is New Zealand.'})

    @property
    def location(self):
        if not self.country:
            return " - "

        loc = self.get_region_display() or self.get_country_display()

        if self.country == 'NZ':
            return loc
        else:
            flag = static(f'flags/{self.country.lower()}.png')
            return format_html(
                '<img src="{}" /> {}',
                flag, loc
            )

    @cached_property
    def structured_data(self):
        return {
            '@type': 'Person',
            '@id': 'https://furry.nz/' + self.get_absolute_url(),
            'name': self.user
        }


__all__ = ['Profile']
