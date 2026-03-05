from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, UpdateView

from allauth.account.views import PasswordResetView, SignupView
from allauth.mfa.base.views import AuthenticateView
from allauth.mfa.models import Authenticator
from csp_helpers.mixins import CSPViewMixin
from oidc_provider.models import UserConsent

from apps.accounts.forms import UserForm


class MFAAuthenticateView(AuthenticateView):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        user = self.stage.login.user
        ret["user_authenticator_types"] = set(
            Authenticator.objects.filter(user=user).values_list("type", flat=True)
        )
        return ret


class CSPSignupView(CSPViewMixin, SignupView):
    pass


class CSPPasswordResetView(CSPViewMixin, PasswordResetView):
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
