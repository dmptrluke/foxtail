from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import JsonResponse
from django.views import View


class AutocompleteView(LoginRequiredMixin, View):
    model = None
    search_fields = []

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        qs = self.model.objects.all()
        if q:
            query = models.Q()
            for field in self.search_fields:
                query |= models.Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)
        return qs[:20]

    def get(self, request, *args, **kwargs):
        results = [{'id': obj.pk, 'text': str(obj)} for obj in self.get_queryset()]
        return JsonResponse({'results': results})
