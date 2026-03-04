def userinfo(claims, user):
    """
    Populates standard OpenID Connect claims
    """
    claims['name'] = getattr(user, 'full_name', None)

    # stop defaults
    claims['given_name'] = None
    claims['family_name'] = None

    if user.date_of_birth:
        claims['birthdate'] = user.date_of_birth.isoformat()

    claims['preferred_username'] = user.username
    claims['nickname'] = user.username

    claims['email'] = user.email
    claims['email_verified'] = user.email_verified

    return claims
