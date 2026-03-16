from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator

from imagefield.fields import ImageField as ProcessedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY

from apps.core.fields import AutoSlugField


class Organisation(models.Model):
    TYPE_CHOICES = [
        ('organisation', 'Organisation'),
        ('community', 'Community Group'),
        ('interest', 'Interest Group'),
    ]
    AGE_CHOICES = [
        ('all', 'All Ages'),
        ('13', '13+'),
        ('16', '16+'),
        ('18', '18+'),
    ]
    REGION_CHOICES = [
        ('northland', 'Northland'),
        ('auckland', 'Auckland'),
        ('waikato', 'Waikato'),
        ('bay-of-plenty', 'Bay of Plenty'),
        ('central-ni', 'Central North Island'),
        ('wellington', 'Wellington'),
        ('top-of-the-south', 'Nelson/Marlborough'),
        ('canterbury', 'Canterbury'),
        ('otago', 'Otago'),
        ('southland', 'Southland'),
        ('nationwide', 'Nationwide'),
        ('online', 'Online'),
    ]
    COUNTRY_CHOICES = [
        ('NZ', 'New Zealand'),
        ('AU', 'Australia'),
    ]

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True)

    description = MarkdownField(rendered_field='description_rendered', validator=VALIDATOR_CLASSY, blank=True)
    description_rendered = RenderedMarkdownField()

    logo = ProcessedImageField(upload_to='organisations', blank=True, auto_add_fields=True)
    url = models.URLField(blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    featured = models.BooleanField(default=False)
    group_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='organisation')
    region = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True)
    age_requirement = models.CharField(max_length=3, choices=AGE_CHOICES, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'group'
        verbose_name_plural = 'groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('groups:organisation_detail', kwargs={'slug': self.slug})

    @property
    def has_detail_content(self):
        """Groups with no description or URL are link-only entries in the directory"""
        return bool(self.description_rendered or self.url)

    @cached_property
    def structured_data(self):
        url = settings.SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'Organization',
            '@id': url,
            'name': self.name,
            'url': url,
            'mainEntityOfPage': url,
        }
        if self.description_rendered:
            data['description'] = Truncator(strip_tags(self.description_rendered)).chars(200)
        if self.url:
            data['sameAs'] = self.url
        if self.logo:
            logo_url = self.logo.square
            if not logo_url.startswith('http'):
                logo_url = settings.SITE_URL + logo_url
            data['logo'] = {
                '@type': 'ImageObject',
                'url': logo_url,
                'width': 400,
                'height': 400,
            }
        return data


class SocialLink(models.Model):
    PLATFORM_CHOICES = [
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
        ('twitter', 'Twitter / X'),
        ('bluesky', 'Bluesky'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('mastodon', 'Mastodon'),
        ('website', 'Website'),
    ]

    PLATFORM_ICONS = {
        'telegram': 'telegram',
        'discord': 'discord',
        'twitter': 'x',
        'bluesky': 'bluesky',
        'instagram': 'instagram',
        'facebook': 'facebook',
        'mastodon': 'mastodon',
        'website': 'link_variant',
    }

    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.CASCADE,
        related_name='social_links',
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'platform']

    def __str__(self):
        return f'{self.get_platform_display()} - {self.organisation}'

    @property
    def icon_name(self):
        return self.PLATFORM_ICONS.get(self.platform, 'link_variant')

    @property
    def join_label(self):
        """Return the CTA label: 'Visit Website' for websites, 'Join on X' for chat platforms"""
        if self.platform == 'website':
            return 'Visit Website'
        return f'Join on {self.get_platform_display()}'


class EventSeries(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True)

    description = MarkdownField(rendered_field='description_rendered', validator=VALIDATOR_CLASSY, blank=True)
    description_rendered = RenderedMarkdownField()

    logo = ProcessedImageField(upload_to='organisations/series', blank=True, auto_add_fields=True)
    organisation = models.ForeignKey(
        'organisations.Organisation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='series',
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'event series'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('series:eventseries_detail', kwargs={'slug': self.slug})
