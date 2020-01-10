from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import now

from allauth.account.models import EmailAddress

from .validators import UsernameValidator


class User(AbstractUser):
    username_validator = UsernameValidator()

    username = models.CharField(
        'username',
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits, spaces, and @/./+/-/_ only.',
        validators=[username_validator],
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


__all__ = ['User']
