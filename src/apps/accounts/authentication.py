import logging
from contextlib import suppress
from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.base import AuthProcess

from apps.email.rendering import build_message, mjml_template_exists

logger = logging.getLogger(__name__)


def valid_email_or_none(email):
    """Return a valid email address or None"""
    try:
        if email:
            validate_email(email)
            return email
    except ValidationError:
        pass
    return None


class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        full_name = user_field(user, 'full_name')
        email = user_email(user)
        username = user_username(user)
        user_username(user, username or self.generate_unique_username([full_name, email, username, 'user']))

    def render_mail(self, template_prefix, email, context, headers=None):
        if not mjml_template_exists(template_prefix):
            return super().render_mail(template_prefix, email, context, headers)

        to = [email] if isinstance(email, str) else email
        message = build_message(template_prefix, to, context, self.get_from_email(), headers)
        message.subject = self.format_email_subject(message.subject)
        return message


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        username = data.get('username')
        email = data.get('email')

        user = sociallogin.user

        user_username(user, username or '')
        user_email(user, valid_email_or_none(email) or '')

        date_of_birth = data.get('birthdate')
        if date_of_birth:
            with suppress(ValueError):
                user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()  # noqa: DTZ007

        name = data.get('name')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if name:
            user_field(user, 'full_name', name)
        else:
            merged = ' '.join(x for x in [first_name, last_name] if x)
            if merged != '':
                user_field(user, 'full_name', merged)

        return user

    def pre_social_login(self, request, sociallogin):
        if sociallogin.account.provider != 'telegram':
            return
        # A connection must stay bound to the authenticated user, even when a bot link already exists.
        if sociallogin.state.get('process') == AuthProcess.CONNECT:
            from apps.telegram.linking import validate_link

            if request.user.is_authenticated:
                try:
                    validate_link(request.user, int(sociallogin.account.uid))
                except IntegrityError:
                    messages.error(request, 'This account is already linked to a different Telegram identity or user.')
                    raise ImmediateHttpResponse(redirect('socialaccount_connections')) from None
            return
        if sociallogin.is_existing:
            return
        try:
            from apps.telegram.models import TelegramLink

            telegram_id = int(sociallogin.account.uid)
            link = TelegramLink.objects.select_related('user').get(telegram_id=telegram_id)
            sociallogin.connect(request, link.user)
            logger.info('Auto-connected Telegram OAuth for user %s via TelegramLink', link.user.pk)
        except TelegramLink.DoesNotExist:
            pass
        except Exception:
            logger.exception('Error in pre_social_login Telegram auto-connect')
            # Abort signup if a lookup failure prevents resolving an existing account owner.
            raise ImmediateHttpResponse(
                HttpResponseForbidden('Unable to verify your Telegram account link. Please try again.')
            ) from None
