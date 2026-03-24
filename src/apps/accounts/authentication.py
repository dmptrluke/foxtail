import logging
from contextlib import suppress
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import render_to_string

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.email.engine import render_email

logger = logging.getLogger(__name__)

MJML_EMAIL_MAP = {
    'account/email/email_confirmation': 'emails/account/email_confirmation',
    'account/email/password_reset_key': 'emails/account/password_reset_key',
}


def valid_email_or_none(email):
    try:
        if email:
            validate_email(email)
            return email
    except ValidationError:
        pass
    return None


class AccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        overrides the base populate_username to not make use of first_name and last_name
        """
        full_name = user_field(user, 'full_name')
        email = user_email(user)
        username = user_username(user)
        user_username(user, username or self.generate_unique_username([full_name, email, username, 'user']))

    def render_mail(self, template_prefix, email, context, headers=None):
        from apps.core.models import SiteSettings

        context['conf'] = SiteSettings.get_solo()
        mjml_template = MJML_EMAIL_MAP.get(template_prefix)
        if mjml_template is None:
            return super().render_mail(template_prefix, email, context, headers)

        to = [email] if isinstance(email, str) else email
        subject = render_to_string(f'{template_prefix}_subject.txt', context)
        subject = ' '.join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        return render_email(
            subject=subject,
            to=to,
            template=mjml_template,
            context=context,
            from_email=self.get_from_email(),
            headers=headers,
        )


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

        # if a full name exists, use that, if not,
        # join first_name and last_name
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
