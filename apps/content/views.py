from django.views.generic import TemplateView, DetailView

from foxtail_blog.models import Post
from apps.content.models import *


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()[:3]
        return context


class PageView(DetailView):
    model = Page
    template_name = 'page.html'


__all__ = ['IndexView', 'PageView']
