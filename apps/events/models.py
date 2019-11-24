from django.db import models
from taggit.managers import TaggableManager

from foxtail_blog.fields import MarkdownField, RenderedMarkdownField, ClassyValidator
from versatileimagefield.fields import VersatileImageField, PPOIField


class Event(models.Model):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")

    tags = TaggableManager(blank=True)

    where = models.CharField(max_length=200)
    what = MarkdownField(rendered_field='what_rendered', validator=ClassyValidator)
    what_rendered = RenderedMarkdownField()

    start = models.DateTimeField()
    end = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    image = VersatileImageField(upload_to='events', blank=True, null=True, ppoi_field='image_ppoi')
    image_ppoi = PPOIField()
