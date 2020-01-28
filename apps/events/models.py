from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.timezone import now

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY
from pytz import utc
from slugger import AutoSlugField
from taggit.managers import TaggableManager
from versatileimagefield.fields import PPOIField, VersatileImageField


class Event(models.Model):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")
    slug = AutoSlugField(populate_from='title', unique_for_year='start')
    tags = TaggableManager(blank=True)

    description = MarkdownField(rendered_field='description_rendered', validator=VALIDATOR_CLASSY)
    description_rendered = RenderedMarkdownField()
    url = models.URLField(blank=True)

    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)

    start = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="Time is optional.")
    end = models.DateField(null=True, blank=True, help_text="End date and time are optional.")
    end_time = models.TimeField(null=True, blank=True, help_text="End date and time are optional.")

    image = VersatileImageField(upload_to='events', blank=True, null=True, ppoi_field='image_ppoi')
    image_ppoi = PPOIField()

    created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'year': self.start.year, 'slug': self.slug})

    @property
    def is_ended(self):
        if self.end:
            end = datetime.combine(self.end, self.end_time) if self.end_time else\
                datetime.combine(self.end, datetime.min.time(), tzinfo=utc)
        else:
            end = datetime.combine(self.start, self.end_time) if self.end_time else (self.start + timedelta(days=1))

        return end < now()

    @cached_property
    def structured_data(self):
        url = settings.SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'Event',
            'name': self.title,
            'description': self.description or Truncator(strip_tags(self.description_rendered)).chars(200),
            'startDate': self.start.strftime('%Y-%m-%d'),
            'url': url,
            'mainEntityOfPage': {
                '@type': 'WebPage',
                '@id': url
            },
        }

        if self.end:
            data['endDate'] = self.end.strftime('%Y-%m-%d')

        if self.location:
            data['location'] = {
                '@type': 'Place',
                'name': self.location,
                'address': self.address or self.location,
            }

        if self.image:
            data['image'] = {
                '@type': 'ImageObject',
                'url': settings.SITE_URL + self.image.url,
                'height': self.image.height,
                'width': self.image.width
            }

        return data
