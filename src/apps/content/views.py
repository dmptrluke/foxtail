from django.conf import settings
from django.db.models import Count, Q
from django.utils.timezone import now
from django.views.generic import DetailView, TemplateView

from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.accounts.models import User
from apps.blog.models import Post
from apps.events.models import Event
from apps.organisations.models import Organisation

from .models import Page


class IndexView(StructuredDataMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        current_year = today.year

        post_list = list(
            queryset_filter(Post.objects)
            .select_related('author', 'author__user')
            .annotate(comment_count=Count('comments', filter=Q(comments__approved=True)))
            .all()[:4]
        )
        context['post_list'] = post_list
        context['featured_post'] = post_list[0] if post_list else None

        context['event_list'] = (
            queryset_filter(Event.objects)
            .filter(Q(start__gte=today) | Q(end__gte=today))
            .order_by('start')
            .prefetch_related('interests__user')[:3]
        )

        featured_orgs = list(Organisation.objects.filter(featured=True))
        for org in featured_orgs:
            org.event_count = Event.objects.filter(Q(organisation=org) | Q(series__organisation=org)).distinct().count()
        context['featured_organisations'] = featured_orgs

        context['stats'] = {
            'member_count': User.objects.count(),
            'events_this_year': Event.objects.filter(start__year=current_year).count(),
            'org_count': Organisation.objects.count(),
        }

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
