from datetime import datetime

from django.db.models import Q
from django.views.generic import DetailView, TemplateView

from published.utils import queryset_filter

from apps.events.models import Event
from foxtail_blog.models import Post

from .models import Page


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.today()
        context['post_list'] = queryset_filter(Post.objects).all()[:3]
        context['event_list'] = Event.objects.filter(Q(start__gte=today) | Q(end__gte=today))[:3]
        return context

    @property
    def structured_data(self):
        return {
            '@type': 'WebSite',
            '@id': 'https://furry.nz/#website',
            'name': 'furry.nz',
            'description': 'The resource for New Zealand furries.',
            'url': 'https://furry.nz/',
            'author': {
                '@type': 'Organization',
                '@id': 'https://furry.nz/#organization',
            }
        }


class PageView(DetailView):
    model = Page
    template_name = 'page.html'


__all__ = ['IndexView', 'PageView']
