from urllib.parse import urlencode

from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class CustomOIDCAB(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(CustomOIDCAB, self).create_user(claims)

        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.save()

        return user


def provider_logout(request):
    if request.session['oidc_id_token']:
        data = {
            'id_token_hint': request.session['oidc_id_token'],
            'post_logout_redirect_uri': request.build_absolute_uri('/s/')
        }

        data_encoded = urlencode(data)
        redirect_url = f'{settings.OIDC_SERVER}/connect/endsession?{data_encoded}'
    else:
        redirect_url = f'{settings.OIDC_SERVER}/connect/endsession'

    return redirect_url
