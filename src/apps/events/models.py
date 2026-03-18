import html
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.timezone import now

from imagefield.fields import ImageField as ProcessedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY
from published.models import PublishedModel
from taggit.managers import TaggableManager

from apps.core.fields import AutoSlugField
from apps.core.validators import file_size_validator

logger = logging.getLogger(__name__)

AGE_CHOICES = [
    ('all', 'All Ages'),
    ('13', '13+'),
    ('16', '16+'),
    ('18', '18+'),
]


class EventQuerySet(models.QuerySet):
    def for_organisation(self, org):
        """Filter to events belonging to an org directly or through a series"""
        return self.filter(models.Q(organisation=org) | models.Q(series__organisation=org)).distinct()


class Event(PublishedModel):
    objects = EventQuerySet.as_manager()

    title = models.CharField(max_length=100, help_text='100 characters or fewer.')
    slug = AutoSlugField(populate_from='title', unique_for_year='start')
    tags = TaggableManager(blank=True)

    description = MarkdownField(rendered_field='description_rendered', validator=VALIDATOR_CLASSY)
    description_rendered = RenderedMarkdownField()
    url = models.URLField(blank=True)

    organisation = models.ForeignKey('organisations.Organisation', on_delete=models.SET_NULL, null=True, blank=True)
    series = models.ForeignKey('organisations.EventSeries', on_delete=models.SET_NULL, null=True, blank=True)

    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text='Time is optional.')
    end = models.DateField(null=True, blank=True, help_text='End date and time are optional.')
    end_time = models.TimeField(null=True, blank=True, help_text='End date and time are optional.')

    age_requirement = models.CharField(max_length=3, choices=AGE_CHOICES, blank=True)

    image = ProcessedImageField(
        upload_to='events', blank=True, auto_add_fields=True, validators=[file_size_validator()]
    )

    created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    modified = models.DateTimeField(auto_now=True, verbose_name='date modified')

    class Meta:
        ordering = ['start']

    def clean(self):
        super().clean()
        if self.end and self.end < self.start:
            raise ValidationError({'end': 'End date cannot be before start date.'})
        if self.series and self.series.organisation and self.organisation:
            raise ValidationError(
                {'organisation': 'Events in a series with an organisation cannot also have a direct organisation.'}
            )

    @cached_property
    def resolved_organisation(self):
        """Return the organisation, preferring the series' org over a direct assignment"""
        if self.series and self.series.organisation:
            return self.series.organisation
        return self.organisation

    @property
    def resolved_age_requirement(self):
        """Return age requirement, falling back to the resolved organisation's setting"""
        if self.age_requirement:
            return self.age_requirement
        org = self.resolved_organisation
        if org:
            return org.age_requirement
        return ''

    @property
    def resolved_age_requirement_display(self):
        """Return the human-readable age requirement label, with org fallback"""
        value = self.resolved_age_requirement
        if not value:
            return ''
        return dict(AGE_CHOICES).get(value, value)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'year': self.start.year, 'slug': self.slug})

    @property
    def is_ended(self):
        """Check if the event has ended; events without an end date are assumed over at midnight after start"""
        if self.end:
            end = (
                datetime.combine(self.end, self.end_time, tzinfo=ZoneInfo('Pacific/Auckland'))
                if self.end_time
                else datetime.combine(self.end, datetime.min.time(), tzinfo=ZoneInfo('Pacific/Auckland'))
            )
        else:
            end = (
                datetime.combine(self.start, self.end_time, tzinfo=ZoneInfo('Pacific/Auckland'))
                if self.end_time
                else datetime.combine(
                    self.start + timedelta(days=1), datetime.min.time(), tzinfo=ZoneInfo('Pacific/Auckland')
                )
            )

        return end < now()

    @cached_property
    def structured_data(self):
        url = settings.SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'Event',
            '@id': url,
            'name': self.title,
            'description': self.description
            or Truncator(html.unescape(strip_tags(self.description_rendered))).chars(200),
            'startDate': self.start,
            'url': url,
            'mainEntityOfPage': url,
            'keywords': [tag.name for tag in self.tags.all()],
        }

        if self.end:
            data['endDate'] = self.end

        if self.location:
            place = {
                '@type': 'Place',
                'name': self.location,
                'address': self.address or self.location,
            }
            if self.latitude and self.longitude:
                place['geo'] = {
                    '@type': 'GeoCoordinates',
                    'latitude': float(self.latitude),
                    'longitude': float(self.longitude),
                }
            data['location'] = place

        if self.image:
            try:
                image_url = self.image.card_2x
                if not image_url.startswith('http'):
                    image_url = settings.SITE_URL + image_url
                data['image'] = {
                    '@type': 'ImageObject',
                    'url': image_url,
                    'width': 1200,
                    'height': 630,
                }
            except Exception:
                logger.exception('Missing image for event %s', self.pk)

        org = self.resolved_organisation
        if org:
            org_url = settings.SITE_URL + org.get_absolute_url()
            data['organizer'] = {'@type': 'Organization', '@id': org_url, 'name': org.name, 'url': org_url}

        return data


class EventInterest(models.Model):
    INTERESTED = 'interested'
    GOING = 'going'
    STATUS_CHOICES = [
        (INTERESTED, 'Interested'),
        (GOING, 'Going'),
    ]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='interests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_interests')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=INTERESTED)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'], name='events_eventinterest_event_user_uniq'),
        ]

    def __str__(self):
        return f'{self.user} - {self.event} ({self.status})'
