from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView

from allauth.account.views import SignupView
from csp_helpers.mixins import CSPViewMixin
from oidc_provider.models import UserConsent

from apps.accounts.forms import UserForm


class CSPSignupView(CSPViewMixin, SignupView):
    pass


class UserView(LoginRequiredMixin, UpdateView):
    template_name = 'account/account.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')


class ConsentList(LoginRequiredMixin, ListView):
    template_name = 'account/applications.html'
    context_object_name = 'consent_list'
    model = UserConsent

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).select_related('client')


__all__ = ['UserView', 'ConsentList']
