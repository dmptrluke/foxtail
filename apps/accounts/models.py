from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "User identifier",
        max_length=150,
        unique=True,
        help_text=None,
    )

    display_name = models.CharField(max_length=50)
    profile_URL = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.email}"


__all__ = ['User']
