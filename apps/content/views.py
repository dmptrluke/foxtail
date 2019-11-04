from django.views.generic import TemplateView, DetailView

from apps.content.models import *


class IndexView(TemplateView):
    template_name = "index.html"


class PageView(DetailView):
    model = Page
    template_name = 'page.html'


__all__ = ['IndexView', 'PageView']
