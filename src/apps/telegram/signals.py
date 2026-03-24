import logging

from . import linking

logger = logging.getLogger(__name__)


def _extract_telegram_fields(extra_data):
    """Extract username and first_name from SocialAccount extra_data."""
    # OAuth flow stores data under id_token; bot bridge stores it at top level
    id_token = extra_data.get('id_token', {})
    return {
        'telegram_username': id_token.get('preferred_username', '') or extra_data.get('username', ''),
        'first_name': id_token.get('name', '') or extra_data.get('first_name', ''),
    }


def on_social_account_changed(sender, request, sociallogin, **kwargs):
    if sociallogin.account.provider != 'telegram':
        return
    try:
        fields = _extract_telegram_fields(sociallogin.account.extra_data)
        linking.link(
            user=request.user,
            telegram_id=int(sociallogin.account.uid),
            **fields,
        )
    except Exception:
        logger.exception('Failed to sync TelegramLink for uid %s', sociallogin.account.uid)


def on_social_account_removed(sender, request, socialaccount, **kwargs):
    if socialaccount.provider != 'telegram':
        return
    linking.unlink(int(socialaccount.uid))
