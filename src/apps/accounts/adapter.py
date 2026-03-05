from allauth.idp.oidc.adapter import DefaultOIDCAdapter


class FoxtailOIDCAdapter(DefaultOIDCAdapter):
    scope_display = {
        "openid": "User Identifier",
        "email": "Email Address",
        "profile": "Profile Information",
    }

    def get_issuer(self):
        from django.conf import settings

        return settings.SITE_URL.rstrip("/") + "/openid"

    def get_claims(self, purpose, user, client, scopes, email=None, **kwargs):
        claims = {"sub": self.get_user_sub(client, user)}

        if "email" in scopes:
            claims["email"] = user.email
            claims["email_verified"] = user.email_verified

        if "profile" in scopes:
            claims["name"] = getattr(user, "full_name", None)
            claims["preferred_username"] = user.username
            claims["nickname"] = user.username
            if user.date_of_birth:
                claims["birthdate"] = user.date_of_birth.isoformat()

        return claims
