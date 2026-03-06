import pytest

from apps.accounts.adapter import FoxtailOIDCAdapter
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


# all scopes enabled returns full claims set
def test_claims(user):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'profile', 'email'])

    # given_name and family_name are excluded for privacy
    assert 'given_name' not in claims
    assert 'family_name' not in claims

    # standard fields are mapped from the user model
    assert claims['nickname'] == user.username
    assert claims['email'] == user.email
    assert claims['email_verified'] is False
    assert claims['name'] == user.full_name


# email scope returns only email fields, not profile fields
def test_claims_email_scope_only(user):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'email'])
    assert 'email' in claims
    assert 'email_verified' in claims
    assert 'name' not in claims
    assert 'preferred_username' not in claims


# profile scope returns only profile fields, not email
def test_claims_profile_scope_only(user):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'profile'])
    assert 'name' in claims
    assert 'preferred_username' in claims
    assert 'nickname' in claims
    assert 'email' not in claims


# openid scope alone returns only the sub claim
def test_claims_openid_only(user):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid'])
    assert 'sub' in claims
    assert len(claims) == 1


# null DOB omits the birthdate key entirely rather than returning None
def test_claims_no_birthdate(user):
    user.date_of_birth = None
    user.save()
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'profile'])
    assert 'birthdate' not in claims


# birthdate is returned in ISO 8601 format
def test_claims_with_birthdate():
    from datetime import date

    user = UserFactory(date_of_birth=date(2000, 6, 15))
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'profile'])
    assert claims['birthdate'] == '2000-06-15'


# issuer URL is derived from the SITE_URL setting
def test_get_issuer(settings):
    settings.SITE_URL = 'https://furry.nz'
    adapter = FoxtailOIDCAdapter()
    assert adapter.get_issuer() == 'https://furry.nz/openid'


# trailing slash in SITE_URL is stripped to avoid double-slash
def test_get_issuer_strips_trailing_slash(settings):
    settings.SITE_URL = 'https://furry.nz/'
    adapter = FoxtailOIDCAdapter()
    assert adapter.get_issuer() == 'https://furry.nz/openid'
