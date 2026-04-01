import html
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator

from imagefield.fields import ImageField as ProcessedImageField
from markdownfield.models import MarkdownField, RenderedMarkdownField
from published.models import PublishedModel
from taggit.managers import TaggableManager

from apps.core.validators import VALIDATOR_EXTENDED

logger = logging.getLogger(__name__)


class Author(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_author',
    )
    description = models.TextField(blank=True, help_text='Short bio or tagline.')
    link = models.URLField(blank=True, help_text='Website, social media, etc.')
    avatar = ProcessedImageField(upload_to='blog/authors', blank=True, auto_add_fields=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):
    def link_fields(self):
        """Select only the fields needed to render a post link (title, URL, date)."""
        return self.only('title', 'slug', 'created', 'publish_status', 'live_as_of')

    def with_related_content(self):
        """Prefetch related orgs, series, and events with only their link fields."""
        from django.db.models import Prefetch

        from apps.events.models import Event
        from apps.organisations.models import EventSeries, Organisation

        return self.prefetch_related(
            Prefetch('organisations', queryset=Organisation.objects.link_fields()),
            Prefetch('event_series', queryset=EventSeries.objects.link_fields()),
            Prefetch('events', queryset=Event.objects.link_fields()),
        )


class Post(PublishedModel):
    title = models.CharField(max_length=100, help_text='100 characters or fewer.')
    slug = models.SlugField(
        unique=True,
        help_text='Changing this value after initial creation will break existing post URLs. Must be unique.',
    )
    tags = TaggableManager(blank=True)

    allow_comments = models.BooleanField(default=True)

    author = models.ForeignKey(
        'foxtail_blog.Author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='date created')
    modified = models.DateTimeField(auto_now=True, verbose_name='date modified')

    image = ProcessedImageField(upload_to='blog', blank=True, auto_add_fields=True)

    description = models.TextField(max_length=140, blank=True, help_text='140 characters or fewer.')

    text = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_EXTENDED)
    text_rendered = RenderedMarkdownField()

    organisations = models.ManyToManyField('organisations.Organisation', blank=True)
    event_series = models.ManyToManyField('organisations.EventSeries', blank=True)
    events = models.ManyToManyField('events.Event', blank=True)

    objects = PostQuerySet.as_manager()

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
            'description': self.description or Truncator(html.unescape(strip_tags(self.text_rendered))).chars(200),
            'author': {'@type': 'Person', 'name': self.author.name} if self.author else None,
            'datePublished': self.created,
            'dateModified': self.modified,
            'publisher': {'@id': f'{settings.SITE_URL}/#organization'},
            'url': url,
            'mainEntityOfPage': url,
            'keywords': [tag.name for tag in self.tags.all()],
        }
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
                logger.exception('Missing image for post %s', self.pk)

        about = []
        for org in self.organisations.all():
            org_url = settings.SITE_URL + org.get_absolute_url()
            about.append({'@type': 'Organization', '@id': org_url, 'name': org.name, 'url': org_url})
        for event in self.events.all():
            event_url = settings.SITE_URL + event.get_absolute_url()
            about.append({'@type': 'Event', '@id': event_url, 'name': event.title, 'url': event_url})
        if about:
            data['about'] = about

        return data


class CommentQuerySet(models.QuerySet):
    def with_author_display(self):
        """Select the comment's author with only the fields needed for rendering."""
        return self.select_related('author').only(
            'id',
            'post_id',
            'text',
            'created',
            'approved',
            'author__id',
            'author__username',
            'author__avatar',
            'author__avatar_width',
            'author__avatar_height',
            'author__avatar_ppoi',
        )


class Comment(models.Model):
    post = models.ForeignKey('foxtail_blog.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    text = models.TextField(max_length=280, help_text='280 characters or fewer.')
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    objects = CommentQuerySet.as_manager()

    def __str__(self):
        return self.text
