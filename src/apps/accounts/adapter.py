import uuid

from django.conf import settings

from allauth.idp.oidc.adapter import DefaultOIDCAdapter

from apps.accounts.models import User


class FoxtailOIDCAdapter(DefaultOIDCAdapter):
    scope_display = {
        'openid': 'User Identifier',
        'email': 'Email Address',
        'profile': 'Profile Information',
        'verification': 'Verification Status',
    }

    def get_issuer(self):
        return settings.SITE_URL.rstrip('/') + '/openid'

    def get_user_sub(self, client, user):
        if client.metadata.legacy_sub:
            return str(user.pk)
        return str(user.uuid)

    def get_user_by_sub(self, client, sub):
        if client.metadata.legacy_sub:
            try:
                pk = int(sub)
            except (ValueError, TypeError):
                return None
            user = User.objects.filter(pk=pk).first()
        else:
            try:
                uuid_val = uuid.UUID(sub)
            except (ValueError, TypeError):
                return None
            user = User.objects.filter(uuid=uuid_val).first()

        if not user or not user.is_active:
            return None
        return user

    def get_claims(self, purpose, user, client, scopes, email=None, **kwargs):
        claims = {'sub': self.get_user_sub(client, user)}

        if 'email' in scopes:
            claims['email'] = user.email
            claims['email_verified'] = user.email_verified

        if 'profile' in scopes:
            claims['name'] = getattr(user, 'full_name', None)
            claims['preferred_username'] = user.username
            claims['nickname'] = user.username
            if user.date_of_birth:
                claims['birthdate'] = user.date_of_birth.isoformat()

        if 'verification' in scopes:
            claims['verified'] = user.is_verified

        return claims
