from django.db import models
from django.urls import reverse

from markdownfield.fields import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY
from taggit.managers import TaggableManager
from versatileimagefield.fields import PPOIField, VersatileImageField


class Event(models.Model):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")

    tags = TaggableManager(blank=True)

    where = models.CharField(max_length=200)
    what = MarkdownField(rendered_field='what_rendered', validator=VALIDATOR_CLASSY)
    what_rendered = RenderedMarkdownField()

    url = models.URLField(blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, help_text="End date is optional.")

    image = VersatileImageField(upload_to='events', blank=True, null=True, ppoi_field='image_ppoi')
    image_ppoi = PPOIField()

    created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    class Meta:
        ordering = ["start"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'year': self.start.year, 'pk': self.pk})
