from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('email address', blank=False)

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True)

    display_name = models.CharField(max_length=50)
    profile_URL = models.CharField(max_length=25)

    def __str__(self):
        return f"{self.username}"


__all__ = ['User']
