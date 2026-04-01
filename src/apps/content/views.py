from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils.timezone import now
from django.views.generic import DetailView, TemplateView

from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.blog.models import Post
from apps.core.models import SiteSettings
from apps.events.models import Event, EventInterest
from apps.organisations.models import Organisation

from .models import Page


class IndexView(StructuredDataMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()
        context['post_list'] = queryset_filter(Post.objects).all()[:3]
        event_list = list(queryset_filter(Event.objects).not_ended().for_homepage()[:3])
        context['event_list'] = event_list

        context['featured_organisations'] = Organisation.objects.filter(featured=True).with_social_links()[:6]

        if event_list:
            context['days_until'] = (event_list[0].start - today).days

        if getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            self._add_dashboard_context(context, today)

        return context

    def _add_dashboard_context(self, context, today):
        from allauth.mfa.models import Authenticator

        user = self.request.user

        user_events = list(
            EventInterest.objects.filter(user=user)
            .filter(Q(event__start__gte=today) | Q(event__end__gte=today))
            .select_related('event')
            .order_by('event__start')
        )
        context['user_event_count'] = len(user_events)
        first_interest = user_events[0] if user_events else None
        if first_interest:
            context['user_next_event'] = first_interest.event
            context['user_next_event_days'] = (first_interest.event.start - today).days

        context['org_count'] = cache.get_or_set('org_count', Organisation.objects.count, 86400)

        has_mfa = Authenticator.objects.filter(user=user).exclude(type=Authenticator.Type.RECOVERY_CODES).exists()
        account_age = (now() - user.date_joined).days
        context['show_mfa_nudge'] = not has_mfa and account_age < 30

    def get_structured_data(self):

        s = SiteSettings.get_solo()
        return {
            '@type': 'WebSite',
            '@id': f'{settings.SITE_URL}/#website',
            'name': s.org_name,
            'description': s.org_description,
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
