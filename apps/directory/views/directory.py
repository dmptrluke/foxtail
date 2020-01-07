from django.views.generic import TemplateView

from apps.directory.models import Profile


class DirectoryIndex(TemplateView):
    template_name = 'directory/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_list'] = Profile.objects.all()
        return context


__all__ = ["DirectoryIndex"]
