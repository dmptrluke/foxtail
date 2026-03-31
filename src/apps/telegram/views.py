import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import handlers, linking
from .models import LinkToken, TelegramLink

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Link confirmation views
# ---------------------------------------------------------------------------


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
                username=link_token.username,
                name=link_token.name,
            )
        except IntegrityError:
            messages.error(request, 'This account is already linked.')
            return redirect('account_profile')

        link_token.delete()
        messages.success(request, 'Your Telegram account has been linked successfully.')
        return redirect('account_profile')


# ---------------------------------------------------------------------------
# Telegram webhook
# ---------------------------------------------------------------------------

COMMANDS = {
    'start': handlers.cmd_start,
    'link': handlers.cmd_link,
    'status': handlers.cmd_status,
    'unlink': handlers.cmd_unlink,
    'help': handlers.cmd_help,
    'ping': handlers.cmd_ping,
}


@csrf_exempt
@require_POST
def telegram_webhook(request):
    secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return HttpResponseForbidden()

    try:
        update = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return HttpResponse(status=400)

    _handle_update(update)
    return HttpResponse('ok')


def _handle_update(update):
    message = update.get('message')
    if not message:
        return

    from_user = message.get('from', {})
    _sync_user_data(from_user)

    text = message.get('text', '')
    if not text.startswith('/'):
        return

    command = text.split()[0].split('@')[0].lstrip('/')
    chat_id = message['chat']['id']
    chat_type = message['chat']['type']

    handler = COMMANDS.get(command)
    if handler:
        handler(chat_id=chat_id, chat_type=chat_type, from_user=from_user)


def _sync_user_data(from_user):
    """Update stored username/name from the incoming message."""
    telegram_id = from_user.get('id')
    if not telegram_id:
        return
    try:
        name = f'{from_user.get("first_name", "")} {from_user.get("last_name", "")}'.strip()
        TelegramLink.objects.filter(telegram_id=telegram_id).update(
            username=from_user.get('username', ''),
            name=name,
        )
    except Exception:
        logger.exception('Failed to sync user data for telegram_id=%s', telegram_id)
