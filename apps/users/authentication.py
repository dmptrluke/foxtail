from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from .models import Profile

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
