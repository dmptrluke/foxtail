from django.db import models
from django.urls import reverse

from markdownx.models import MarkdownxField
from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField, PPOIField


class Post(models.Model):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")
    slug = models.SlugField(
        unique=True,
        help_text="Changing this value after initial creation will break existing "
        "post URLs. Must be unique.",
    )
    tags = TaggableManager()

    author = models.CharField(max_length=50, help_text="50 characters or fewer.")
    created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    image = VersatileImageField(upload_to='blog', blank=True, null=True, ppoi_field='image_ppoi')
    image_ppoi = PPOIField()

    text = MarkdownxField()

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
