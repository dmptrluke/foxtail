from django.views.generic import TemplateView


class DirectoryIndex(TemplateView):
    template_name = 'directory/index.html'


__all__ = ["DirectoryIndex"]
