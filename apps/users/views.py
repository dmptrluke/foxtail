from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from mozilla_django_oidc.views import OIDCLogoutView


class UserView(TemplateView):
    template_name = "profile.html"


class LogoutView(OIDCLogoutView):
    def get(self, request):
        return self.post(request)
