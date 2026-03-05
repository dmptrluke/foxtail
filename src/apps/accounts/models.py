from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now

from allauth.account.models import EmailAddress
from versatileimagefield.fields import VersatileImageField

from .validators import username_validators


class User(AbstractUser):
    username = models.CharField(
        'username',
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits, spaces, and @/./+/-/_ only.',
        validators=username_validators,
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    email = models.EmailField('email address', blank=False)

    full_name = models.CharField(max_length=120, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def clean(self):
        if self.date_of_birth:
            if self.date_of_birth >= now().date():
                raise ValidationError({'date_of_birth': 'Date of birth can not be in the future.'})

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.username

    @cached_property
    def email_verified(self):
        """ check if the users main email is verified """
        return EmailAddress.objects.filter(user=self,
                                           email=self.email,
                                           verified=True,
                                           primary=True).exists()

    def __str__(self):
        return f"{self.username}"


class ClientMetadata(models.Model):
    """Extra metadata for OIDC clients that allauth's Client model doesn't provide."""

    client = models.OneToOneField(
        "allauth_idp_oidc.Client",
        on_delete=models.CASCADE,
        related_name="metadata",
    )
    logo = VersatileImageField(upload_to="oidc/clients/", blank=True)
    website_url = models.URLField(blank=True)
    terms_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = "client metadata"
        verbose_name_plural = "client metadata"

    def __str__(self):
        return f"Metadata for {self.client.name}"


__all__ = ['User', 'ClientMetadata']
