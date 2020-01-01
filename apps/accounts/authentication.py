from datetime import datetime

from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import valid_email_or_none
from allauth_2fa.adapter import OTPAdapter


class AccountAdapter(OTPAdapter):
    def populate_username(self, request, user):
        """
        overrides the base populate_username to not make use of first_name and last_name
        """
        full_name = user_field(user, 'full_name')
        email = user_email(user)
        username = user_username(user)
        user_username(
            user,
            username or self.generate_unique_username([full_name, email, username, 'user'])
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
            try:
                parsed = datetime.strptime(date_of_birth, "%Y-%m-%d")
                user.date_of_birth = parsed
            except ValueError:
                pass

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
