from django.db import models
from django.urls import reverse

from markdownx.models import MarkdownxField

from apps.core.fields import MarkdownField


class Page(models.Model):
    title = models.CharField(max_length=100, help_text="100 characters or fewer.")
    subtitle = models.CharField(
        max_length=100, blank=True, default='', help_text="100 characters or fewer. Optional."
    )
    modified = models.DateTimeField(auto_now=True, verbose_name="date modified")

    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    show_in_menu = models.BooleanField(
        default=True, help_text="Set this if you want the page " "to be listed in site navigation."
    )
    slug = models.SlugField(
        unique=True,
        help_text="Changing this value after initial creation will break existing "
        "page URLs. Must be unique.",
    )

    body = MarkdownField(rendered_field='body_rendered')
    body_rendered = models.TextField(blank=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page-detail', kwargs={'slug': self.slug})


__all__ = ['Page']
