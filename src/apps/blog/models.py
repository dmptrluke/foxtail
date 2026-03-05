from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_CLASSY
from published.models import PublishedModel
from rules.contrib.models import RulesModel
from taggit.managers import TaggableManager
from versatileimagefield.fields import PPOIField, VersatileImageField

from . import rules


class Post(PublishedModel):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")
    slug = models.SlugField(unique=True, help_text="Changing this value after initial creation will break existing "
                                                   "post URLs. Must be unique.")
    tags = TaggableManager(blank=True)

    allow_comments = models.BooleanField(default=True)

    author = models.CharField(max_length=50, help_text="50 characters or fewer.")
    created = models.DateTimeField(auto_now_add=True, verbose_name="date created")
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    image = VersatileImageField(upload_to='blog', blank=True, null=True, ppoi_field='image_ppoi')
    image_ppoi = PPOIField()

    description = models.TextField(max_length=140, blank=True, help_text="140 characters or fewer.")

    text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_CLASSY)
    text_rendered = RenderedMarkdownField()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    @cached_property
    def structured_data(self):
        url = settings.SITE_URL + self.get_absolute_url()
        data = {
            '@type': 'BlogPosting',
            'headline': self.title,
            'description': self.description or Truncator(strip_tags(self.text_rendered)).chars(200),
            'author': {
                '@type': 'Person',
                'name': self.author
            },
            'datePublished': self.created.strftime('%Y-%m-%d'),
            'dateModified': self.modified.strftime('%Y-%m-%d'),
            'publisher': None,
            'url': url,
            'mainEntityOfPage': {
                '@type': 'WebPage',
                '@id': url
            },
        }
        if self.image:
            data['image'] = {
                '@type': 'ImageObject',
                'url': settings.SITE_URL + self.image.url,
                'height': self.image.height,
                'width': self.image.width
            }

        return data


class Comment(RulesModel):
    post = models.ForeignKey('foxtail_blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    text = models.TextField(max_length=280, help_text="280 characters or fewer.")
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        rules_permissions = {
            'change': rules.is_owner_or_editor,
            'delete': rules.is_owner_or_moderator
        }

    def __str__(self):
        return self.text
