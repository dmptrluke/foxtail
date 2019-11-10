from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class UserView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"


__all__ = ['UserView']
