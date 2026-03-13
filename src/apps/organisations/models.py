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
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True)

    description = MarkdownField(rendered_field='description_rendered', validator=VALIDATOR_CLASSY, blank=True)
    description_rendered = RenderedMarkdownField()

    logo = ProcessedImageField(upload_to='organisations', blank=True, auto_add_fields=True)
    url = models.URLField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organisations:organisation_detail', kwargs={'slug': self.slug})

    @cached_property
    def structured_data(self):
        url = settings.SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'Organization',
            'name': self.name,
            'url': url,
            'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
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
