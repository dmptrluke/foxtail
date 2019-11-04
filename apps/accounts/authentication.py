import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

LOGGER = logging.getLogger(__name__)


class CustomOIDCAB(OIDCAuthenticationBackend):
    """
    A custom OIDCAuthenticationBackend that uses the sub as an identifier, not email.
    """

    def filter_users_by_claims(self, claims):
        """Return all users matching the specified identifier."""
        username = claims.get('sub')
        if not username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username__iexact=username)

    def get_or_create_user(self, access_token, id_token, payload):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        user_info = self.get_userinfo(access_token, id_token, payload)

        username = user_info.get('sub')

        claims_verified = self.verify_claims(user_info)
        if not claims_verified:
            msg = 'Claims verification failed'
            raise SuspiciousOperation(msg)

        # identifier based filtering
        users = self.filter_users_by_claims(user_info)

        if len(users) == 1:
            return self.update_user(users[0], user_info)
        elif len(users) > 1:
            # In the rare case that two user accounts have the same identifier,
            # bail. This really shouldn't happen. Something is wrong.
            raise SuspiciousOperation('Multiple users returned')

        elif self.get_settings('OIDC_CREATE_USER', True):
            # We have no user. Let's make one!
            return self.create_user(user_info)
        else:
            # ...or not
            LOGGER.debug('Login failed: No user with identifier %s found, and '
                         'OIDC_CREATE_USER is False', username)

    def create_user(self, claims):
        username = claims.get('sub')
        email = claims.get('email')

        user = self.UserModel.objects.create_user(username, email)

        user.set_unusable_password()
        user.email = claims.get('email', '')
        user.display_name = claims.get('email', '')
        user.save()

        return user

    def update_user(self, user, claims):
        user.set_unusable_password()
        user.email = claims.get('email', '')
        user.display_name = claims.get('email', '')
        user.save()

        return user


def provider_logout(request):
    if request.session.get('oidc_id_token', None):
        data = {
            'id_token_hint': request.session['oidc_id_token'],
            'post_logout_redirect_uri': request.build_absolute_uri('/')
        }

        data_encoded = urlencode(data)
        redirect_url = f'{settings.OIDC_SERVER}/connect/endsession?{data_encoded}'
    else:
        redirect_url = f'{settings.OIDC_SERVER}/connect/endsession'

    return redirect_url
