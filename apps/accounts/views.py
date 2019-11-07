from django.views.generic import TemplateView
from mozilla_django_oidc.views import OIDCLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin


class UserView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"


class LogoutView(LoginRequiredMixin, OIDCLogoutView):
    def get(self, request):
        return self.post(request)


__all__ = ['UserView', 'LogoutView']
