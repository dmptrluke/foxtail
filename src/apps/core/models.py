from django.db import models

from solo.models import SingletonModel


class SiteSettings(SingletonModel):
    """Admin-editable site branding and configuration."""

    org_name = models.CharField('Organisation Name', max_length=100, default='furry.nz')
    org_description = models.TextField(
        'Organisation Description',
        blank=True,
        help_text='Short description for structured data and SEO.',
    )
    theme_color = models.CharField(
        'Theme Color',
        max_length=7,
        default='#281e33',
        help_text='Hex color for browser theme-color meta tag.',
    )
    facebook_app_id = models.CharField('Facebook App ID', max_length=50, blank=True)
    google_site_verification = models.CharField(
        'Google Site Verification',
        max_length=100,
        blank=True,
        help_text='Content value from the Google Search Console meta tag.',
    )

    telegram_url = models.URLField('Telegram URL', blank=True)
    bluesky_url = models.URLField('Bluesky URL', blank=True)
    x_url = models.URLField('X URL', blank=True)

    contact_email = models.EmailField(
        'Contact Email', blank=True, help_text='Public contact address shown on contact page.'
    )

    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'

    def __str__(self):
        return 'Site Settings'
