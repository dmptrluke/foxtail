from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now

from imagefield.fields import ImageField as ProcessedImageField

from apps.core.validators import file_size_validator

from . import rules  # noqa: F401
from .validators import username_validators


class User(AbstractUser):
    username = models.CharField(
        'username',
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits, spaces, and @/./+/-/_ only.',
        validators=username_validators,
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )

    email = models.EmailField('email address', blank=False)

    full_name = models.CharField(max_length=120, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    avatar = ProcessedImageField(
        upload_to='avatars',
        blank=True,
        auto_add_fields=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), file_size_validator()],
    )

    def clean(self):
        if self.date_of_birth and self.date_of_birth >= now().date():
            raise ValidationError({'date_of_birth': 'Date of birth can not be in the future.'})

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.username

    @cached_property
    def email_verified(self):
        from allauth.account.models import EmailAddress

        return EmailAddress.objects.filter(user=self, email=self.email, verified=True, primary=True).exists()

    @cached_property
    def is_verified(self):
        return Verification.objects.filter(user=self).exists()

    def __str__(self):
        return f'{self.username}'


class Verification(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='verification',
    )
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='verifications_given',
    )
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} verified by {self.verified_by}'


class ClientMetadata(models.Model):
    """Extra metadata for OIDC clients that allauth's Client model doesn't provide."""

    client = models.OneToOneField(
        'allauth_idp_oidc.Client',
        on_delete=models.CASCADE,
        related_name='metadata',
    )
    logo = ProcessedImageField(upload_to='oidc/clients/', blank=True, auto_add_fields=True)
    website_url = models.URLField(blank=True)
    terms_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'client metadata'
        verbose_name_plural = 'client metadata'

    def __str__(self):
        return f'Metadata for {self.client.name}'


__all__ = ['ClientMetadata', 'User', 'Verification']
