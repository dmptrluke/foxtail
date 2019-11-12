def userinfo(claims, user):
    """
    Populates standard OpenID Connect claims
    """
    if user.first_name or user.last_name:
        claims['name'] = " ".join([user.first_name, user.last_name])

    if user.first_name:
        claims['given_name'] = user.first_name

    if user.last_name:
        claims['family_name'] = user.last_name

    claims['preferred_username'] = user.username
    claims['email'] = user.email

    return claims
