from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

from allauth.account.models import EmailAddress
from allauth.account.views import PasswordResetView, SignupView
from allauth.idp.oidc.models import Client as OIDCClient
from allauth.idp.oidc.models import Token as OIDCToken
from allauth.mfa.base.views import AuthenticateView
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount
from csp_helpers.mixins import CSPViewMixin

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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'account/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        emails = EmailAddress.objects.filter(user=user)
        ctx['primary_email'] = emails.filter(primary=True).first()
        ctx['email_count'] = emails.count()

        authenticator_types = set(
            Authenticator.objects.filter(user=user)
            .exclude(type=Authenticator.Type.RECOVERY_CODES)
            .values_list('type', flat=True)
        )
        ctx['mfa_enabled'] = len(authenticator_types) > 0
        ctx['mfa_methods'] = authenticator_types

        ctx['app_count'] = (
            OIDCToken.objects.filter(user=user)
            .values('client').distinct().count()
        )

        social_accounts = SocialAccount.objects.filter(user=user)
        ctx['social_count'] = social_accounts.count()
        ctx['social_providers'] = list(social_accounts.values_list('provider', flat=True))

        ctx['has_password'] = user.has_usable_password()

        return ctx


class UserView(LoginRequiredMixin, UpdateView):
    template_name = 'account/settings.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your account details have been updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account_settings')


class ConsentList(LoginRequiredMixin, ListView):
    template_name = 'account/applications.html'
    context_object_name = 'client_list'

    def get_queryset(self):
        return OIDCClient.objects.filter(
            token__user=self.request.user,
        ).distinct()


class ConsentRevoke(LoginRequiredMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(OIDCClient, pk=pk)
        deleted, _ = OIDCToken.objects.filter(user=request.user, client=client).delete()
        if not deleted:
            raise Http404
        messages.success(request, "Application access has been revoked.")
        return redirect('account_application_list')


__all__ = ['DashboardView', 'UserView', 'ConsentList', 'ConsentRevoke']
