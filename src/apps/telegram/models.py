from django.conf import settings
from django.db import models
from django.utils.timezone import now


class TelegramLink(models.Model):
    """Links a Foxtail user account to a Telegram user ID."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='telegram_link',
    )
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    telegram_username = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    linked_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(
        default=False,
        help_text='Bot received 403 when sending to this user',
    )

    class Meta:
        verbose_name = 'telegram link'

    def __str__(self):
        return f'{self.user} -> {self.telegram_id}'


class LinkToken(models.Model):
    """Pending bot-first link: stores Telegram identity until a logged-in user confirms."""

    telegram_id = models.BigIntegerField()
    telegram_username = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(max_length=64, blank=True)
    token = models.CharField(max_length=86, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = 'link token'
        indexes = [
            models.Index(fields=['telegram_id']),
        ]

    def __str__(self):
        return f'{self.telegram_id} ({self.token[:8]}...)'

    @property
    def is_expired(self):
        return now() >= self.expires_at
