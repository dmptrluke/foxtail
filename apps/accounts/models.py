from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from .validators import UsernameValidator


class User(AbstractUser):
    username_validator = UsernameValidator()

    username = models.CharField(
        'username',
        max_length=50,
        unique=True,
        help_text='Required. 50 characters or fewer. Letters, digits, spaces, and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    email = models.EmailField('email address', blank=False)

    full_name = models.CharField(max_length=120, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True)

    profile_URL = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.username}"


__all__ = ['User']
