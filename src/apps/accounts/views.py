import base64
import io
import secrets
import string

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

import segno
from allauth.account.models import EmailAddress
from allauth.account.views import PasswordResetView, SignupView
from allauth.core.ratelimit import consume_or_429
from allauth.idp.oidc.models import Client as OIDCClient
from allauth.idp.oidc.models import Token as OIDCToken
from allauth.mfa.base.views import AuthenticateView
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount
from csp_helpers.mixins import CSPViewMixin
from rules.contrib.views import PermissionRequiredMixin

from apps.accounts.forms import UserForm
from apps.accounts.models import User, Verification


class MFAAuthenticateView(AuthenticateView):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        user = self.stage.login.user
        ret['user_authenticator_types'] = set(Authenticator.objects.filter(user=user).values_list('type', flat=True))
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

        ctx['app_count'] = OIDCToken.objects.filter(user=user).values('client').distinct().count()

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
        messages.success(self.request, 'Your account details have been updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('account_profile_edit')


class ConsentList(LoginRequiredMixin, ListView):
    template_name = 'account/applications.html'
    context_object_name = 'client_list'

    def get_queryset(self):
        return (
            OIDCClient.objects.filter(
                token__user=self.request.user,
            )
            .select_related('metadata')
            .distinct()
        )


class ConsentRevoke(LoginRequiredMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(OIDCClient, pk=pk)
        deleted, _ = OIDCToken.objects.filter(user=request.user, client=client).delete()
        if not deleted:
            raise Http404
        messages.success(request, 'Application access has been revoked.')
        return redirect('account_application_list')


VERIFICATION_TOKEN_TTL = 600  # 10 minutes
VERIFICATION_TOKEN_LENGTH = 8
VERIFICATION_TOKEN_CHARS = string.ascii_uppercase + string.digits


def _generate_token():
    raw = ''.join(secrets.choice(VERIFICATION_TOKEN_CHARS) for _ in range(VERIFICATION_TOKEN_LENGTH))
    return f'{raw[:4]}-{raw[4:]}'


def _cache_key_for_token(token):
    return f'verification_token:{token.replace("-", "").upper()}'


def _cache_key_for_user(user_id):
    return f'verification_user_token:{user_id}'


def _make_qr_data_uri(url):
    qr = segno.make(url)
    buf = io.BytesIO()
    qr.save(buf, kind='svg', scale=4, border=2, dark='#212529')
    encoded = base64.b64encode(buf.getvalue()).decode()
    return f'data:image/svg+xml;base64,{encoded}'


class VerificationView(LoginRequiredMixin, TemplateView):
    template_name = 'account/verification.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            verification = user.verification
            ctx['verification'] = verification
        except Verification.DoesNotExist:
            pass

        existing_token_key = cache.get(_cache_key_for_user(user.pk))
        if existing_token_key:
            token_cache_key = _cache_key_for_token(existing_token_key)
            if cache.get(token_cache_key):
                ctx['token'] = existing_token_key
                ctx['token_ttl'] = cache.ttl(token_cache_key)  # type: ignore[attr-defined]
                from django.conf import settings

                base = settings.SITE_URL.rstrip('/')
                path = reverse('account_verification')
                ctx['qr_data_uri'] = _make_qr_data_uri(f'{base}{path}?code={existing_token_key}')

        ctx['is_verifier'] = user.has_perm('accounts.verify_user')

        code = self.request.GET.get('code', '').strip()
        if code:
            if ctx['is_verifier']:
                ctx['prefilled_code'] = code
            else:
                messages.error(self.request, 'You do not have permission to verify users.')

        return ctx


class GenerateTokenView(LoginRequiredMixin, View):
    def post(self, request):
        resp = consume_or_429(request, action='verify_generate')
        if resp:
            return resp
        user = request.user

        old_token = cache.get(_cache_key_for_user(user.pk))
        if old_token:
            cache.delete(_cache_key_for_token(old_token))

        token = _generate_token()
        cache.set(_cache_key_for_token(token), user.pk, VERIFICATION_TOKEN_TTL)
        cache.set(_cache_key_for_user(user.pk), token, VERIFICATION_TOKEN_TTL)

        return redirect('account_verification')


def _normalize_token(raw):
    normalized = raw.replace('-', '').upper()
    if len(normalized) == VERIFICATION_TOKEN_LENGTH:
        return f'{normalized[:4]}-{normalized[4:]}'
    return raw.upper()


def _resolve_token(request, token_raw):
    if not token_raw:
        messages.error(request, 'Please enter a verification code.')
        return None, None
    formatted = _normalize_token(token_raw)
    target_user_id = cache.get(_cache_key_for_token(formatted))
    if not target_user_id:
        messages.error(request, 'Invalid or expired verification code.')
        return None, None
    # TODO: re-enable self-verification check
    # if target_user_id == request.user.pk:
    #     messages.error(request, 'You cannot verify yourself.')
    #     return None, None
    return get_object_or_404(User, pk=target_user_id), formatted


class ConfirmVerificationView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'account/verification_confirm.html'
    permission_required = 'accounts.verify_user'

    def post(self, request):

        token_raw = request.POST.get('token', '').strip()
        target_user, formatted = _resolve_token(request, token_raw)
        if not target_user:
            return redirect('account_verification')

        already_verified = Verification.objects.filter(user=target_user).exists()
        return self.render_to_response(
            {
                'target_user': target_user,
                'token': formatted,
                'already_verified': already_verified,
            }
        )


class VerifyUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'accounts.verify_user'

    def post(self, request):
        resp = consume_or_429(request, action='verify_submit')
        if resp:
            return resp

        token_raw = request.POST.get('token', '').strip()
        target_user, formatted = _resolve_token(request, token_raw)
        if not target_user:
            return redirect('account_verification')

        _, created = Verification.objects.get_or_create(
            user=target_user,
            defaults={'verified_by': request.user},
        )
        cache.delete(_cache_key_for_token(formatted))
        cache.delete(_cache_key_for_user(target_user.pk))
        if created:
            messages.success(request, f'{target_user.username} has been verified.')
        else:
            messages.info(request, f'{target_user.username} is already verified.')
        return redirect('account_verification')


class UnverifyUserView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = 'accounts.verify_user'

    def post(self, request):
        resp = consume_or_429(request, action='verify_unverify')
        if resp:
            return resp

        token_raw = request.POST.get('token', '').strip()
        target_user, formatted = _resolve_token(request, token_raw)
        if not target_user:
            return redirect('account_verification')

        deleted, _ = Verification.objects.filter(user=target_user).delete()
        if not deleted:
            messages.info(request, f'{target_user.username} is not currently verified.')
        else:
            messages.success(request, f'Verification for {target_user.username} has been removed.')

        cache.delete(_cache_key_for_token(formatted))
        cache.delete(_cache_key_for_user(target_user.pk))
        return redirect('account_verification')


__all__ = [
    'ConfirmVerificationView',
    'ConsentList',
    'ConsentRevoke',
    'DashboardView',
    'GenerateTokenView',
    'UnverifyUserView',
    'UserView',
    'VerificationView',
    'VerifyUserView',
]
