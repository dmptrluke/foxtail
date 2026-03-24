import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from . import linking
from .models import LinkToken, TelegramLink

logger = logging.getLogger(__name__)


class LinkTelegramView(LoginRequiredMixin, View):
    def get(self, request, token):
        link_token = get_object_or_404(LinkToken, token=token)
        if link_token.is_expired:
            messages.error(request, 'This link token has expired. Please run /link again in the bot.')
            return redirect('account_profile')
        return render(
            request,
            'telegram/link_confirm.html',
            {
                'link_token': link_token,
            },
        )


class LinkTelegramConfirmView(LoginRequiredMixin, View):
    def post(self, request):
        token = request.POST.get('token', '')
        link_token = get_object_or_404(LinkToken, token=token)

        if link_token.is_expired:
            messages.error(request, 'This link token has expired. Please run /link again in the bot.')
            return redirect('account_profile')

        if TelegramLink.objects.filter(telegram_id=link_token.telegram_id).exists():
            messages.error(request, 'This Telegram account is already linked to another user.')
            link_token.delete()
            return redirect('account_profile')

        if TelegramLink.objects.filter(user=request.user).exists():
            messages.error(request, 'Your account is already linked to a Telegram account.')
            link_token.delete()
            return redirect('account_profile')

        try:
            linking.link(
                user=request.user,
                telegram_id=link_token.telegram_id,
                telegram_username=link_token.telegram_username,
                first_name=link_token.first_name,
            )
        except IntegrityError:
            messages.error(request, 'This account is already linked.')
            return redirect('account_profile')

        link_token.delete()
        messages.success(request, 'Your Telegram account has been linked successfully.')
        return redirect('account_profile')
