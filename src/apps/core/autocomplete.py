from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.views import View

from .querysets import filter_by_parent


class AutocompleteView(LoginRequiredMixin, View):
    """Return JSON autocomplete results with optional parent filtering"""

    model = None
    search_fields = ()
    parent_field = None

    def get_queryset(self):
        """Apply parent and text filters before the response limits results"""
        qs = self.model.objects.all()
        # Omitted parents let independent selectors use the same endpoint.
        if self.parent_field and self.parent_field in self.request.GET:
            qs = filter_by_parent(qs, self.parent_field, self.request.GET[self.parent_field])
        q = self.request.GET.get('q', '')
        if q:
            query = models.Q()
            for field in self.search_fields:
                query |= models.Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)
        return qs

    def get(self, request, *args, **kwargs):
        results = [{'id': obj.pk, 'text': str(obj)} for obj in self.get_queryset()[:20]]
        return JsonResponse({'results': results})
