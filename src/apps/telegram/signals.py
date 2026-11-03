import logging

from . import linking
from .models import TelegramLink

logger = logging.getLogger(__name__)


def _extract_telegram_fields(extra_data):
    """Extract username and name from stored sign-in data"""
    if not isinstance(extra_data, dict):
        return {'username': '', 'name': ''}
    data = extra_data.get('userinfo') or extra_data.get('id_token') or extra_data
    if not isinstance(data, dict):
        data = extra_data
    username = data.get('preferred_username') or extra_data.get('username') or ''
    name = data.get('name') or extra_data.get('name') or ''
    return {
        'username': username[:32] if isinstance(username, str) else '',
        'name': name[:64] if isinstance(name, str) else '',
    }


def on_social_account_changed(sender, request, sociallogin=None, **kwargs):
    if sociallogin is None or sociallogin.account.provider != 'telegram':
        return
    try:
        fields = _extract_telegram_fields(sociallogin.account.extra_data)
        linking.link(
            user=sociallogin.user,
            telegram_id=int(sociallogin.account.uid),
            **fields,
        )
    except Exception:
        # A bot-link failure must not revoke a valid social login.
        logger.exception('Failed to sync TelegramLink for uid %s', sociallogin.account.uid)


def on_social_account_removed(sender, request, socialaccount, **kwargs):
    if socialaccount.provider != 'telegram':
        return
    # Allauth has already removed the sign-in account; only remove the same owner's bot link.
    TelegramLink.objects.filter(telegram_id=int(socialaccount.uid), user_id=socialaccount.user_id).delete()
