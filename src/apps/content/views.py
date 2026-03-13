from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now
from django.views.generic import DetailView, TemplateView

from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.blog.models import Post
from apps.events.models import Event

from .models import Page


class IndexView(StructuredDataMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        context['post_list'] = queryset_filter(Post.objects).select_related('author').all()[:3]
        context['event_list'] = Event.objects.filter(Q(start__gte=today) | Q(end__gte=today))[:3]
        return context

    def get_structured_data(self):
        return {
            '@type': 'WebSite',
            '@id': f'{settings.SITE_URL}/#website',
            'name': 'furry.nz',
            'description': 'The resource for New Zealand furries.',
            'url': f'{settings.SITE_URL}/',
            'author': {
                '@type': 'Organization',
                '@id': f'{settings.SITE_URL}/#organization',
            },
        }


class PageView(DetailView):
    model = Page
    template_name = 'page.html'


__all__ = ['IndexView', 'PageView']
