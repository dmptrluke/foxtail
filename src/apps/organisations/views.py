from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.timezone import localdate
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.blog.models import Post
from apps.events.models import Event

from .forms import SocialLinkRedirectForm
from .models import EventSeries, Organisation, SocialLink


class OrganisationListView(StructuredDataMixin, ListView):
    model = Organisation
    template_name = 'organisations/organisation_list.html'
    context_object_name = 'organisation_list'

    def get_queryset(self):
        qs = Organisation.objects.with_social_links()
        region = self.request.GET.get('region')
        if region and region in dict(Organisation.REGION_CHOICES):
            qs = qs.filter(Q(region=region) | Q(region='nationwide') | Q(region='online'))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_orgs = context['organisation_list']
        context['featured'] = [o for o in all_orgs if o.featured]
        context['organisations'] = [o for o in all_orgs if o.group_type == 'organisation' and not o.featured]
        context['communities'] = [o for o in all_orgs if o.group_type == 'community' and not o.featured]
        context['interest_groups'] = [o for o in all_orgs if o.group_type == 'interest' and not o.featured]
        active_regions = {o.region for o in all_orgs if o.region}
        context['regions'] = [(k, v) for k, v in Organisation.REGION_CHOICES if k in active_regions]
        context['current_region'] = self.request.GET.get('region', '')
        return context

    def get_structured_data(self):
        return {
            '@type': 'CollectionPage',
            'name': 'Groups',
            'description': 'Find your community in New Zealand',
            'url': self.request.build_absolute_uri(),
        }


class OrganisationDetailView(DetailView):
    model = Organisation
    template_name = 'organisations/organisation_detail.html'

    def get_queryset(self):
        return Organisation.objects.with_relations()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.object
        series = org.series.all()
        social_links = org.social_links.all()
        events = (
            queryset_filter(Event.objects.for_organisation(org))
            .with_relations()
            .order_by(F('series__name').asc(nulls_last=True), '-start')
        )
        posts = (
            queryset_filter(Post.objects)
            .filter(Q(organisations=org) | Q(events__in=events) | Q(event_series__in=series))
            .distinct()
        )
        next_event = (
            queryset_filter(Event.objects.for_organisation(org))
            .with_relations()
            .filter(Q(end__gte=localdate()) | Q(end__isnull=True, start__gte=localdate()))
            .order_by('start')
            .first()
        )
        context['series'] = series
        context['social_links'] = social_links
        context['events'] = events
        context['posts'] = posts
        context['next_event'] = next_event
        context['has_content'] = bool(org.description_rendered or events or posts or series or next_event)
        return context


class EventSeriesDetailView(DetailView):
    model = EventSeries
    template_name = 'organisations/eventseries_detail.html'

    def get_queryset(self):
        return EventSeries.objects.select_related('organisation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.object
        events = queryset_filter(Event.objects).with_relations().filter(series=series).order_by('-start')
        posts = queryset_filter(Post.objects).filter(Q(event_series=series) | Q(events__in=events)).distinct()
        context['events'] = events
        context['posts'] = posts
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SocialLinkRedirectView(View):
    def get(self, request, pk):
        link = get_object_or_404(SocialLink, pk=pk)
        if request.user.is_authenticated:
            SocialLink.objects.filter(pk=pk).update(click_count=F('click_count') + 1)
            return HttpResponseRedirect(link.url)
        form = SocialLinkRedirectForm(csp_nonce=request.csp_nonce)
        return render(
            request,
            'organisations/social_link_redirect.html',
            {
                'form': form,
                'link': link,
            },
        )

    def post(self, request, pk):
        link = get_object_or_404(SocialLink, pk=pk)
        form = SocialLinkRedirectForm(request.POST, csp_nonce=request.csp_nonce)
        if form.is_valid():
            SocialLink.objects.filter(pk=pk).update(click_count=F('click_count') + 1)
            return HttpResponseRedirect(link.url)
        return render(
            request,
            'organisations/social_link_redirect.html',
            {
                'form': form,
                'link': link,
            },
        )
