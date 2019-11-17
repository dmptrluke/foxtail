from allauth.account.utils import user_email, user_field, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import valid_email_or_none
from allauth_2fa.adapter import OTPAdapter

from datetime import datetime


class AccountAdapter(OTPAdapter):
    pass


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # get data, process data
        username = data.get('username')
        email = data.get('email')

        user = sociallogin.user

        user_username(user, username or '')
        user_email(user, valid_email_or_none(email) or '')

        _date_of_birth = data.get('birthdate')
        if _date_of_birth:
            try:
                date_of_birth = datetime.strptime(_date_of_birth, "%Y-%m-%d")
                user_field(user, 'date_of_birth', date_of_birth)
            except ValueError:
                pass

        name = data.get('name')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if name:
            user_field(user, 'full_name', name)
        else:
            if first_name:
                merged_name = ' '.join([first_name, last_name])
                user_field(user, 'full_name', merged_name)

        gender = data.get('gender')
        if name:
            user_field(user, 'gender', gender.title())

        return user
