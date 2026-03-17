from django.db import models

from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    """Admin-editable site branding and configuration."""

    org_name = models.CharField(max_length=100, default='furry.nz')
    org_description = models.TextField(
        blank=True,
        help_text='Short description for structured data and SEO.',
    )
    theme_color = models.CharField(
        max_length=7,
        default='#281e33',
        help_text='Hex color for browser theme-color meta tag.',
    )
    facebook_app_id = models.CharField(max_length=50, blank=True)

    telegram_url = models.URLField(blank=True)
    bluesky_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)

    contact_email = models.EmailField(blank=True, help_text='Public contact address shown on contact page.')

    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'

    def __str__(self):
        return 'Site Settings'
