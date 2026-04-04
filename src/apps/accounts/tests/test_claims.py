import uuid

import pytest

from apps.accounts.adapter import FoxtailOIDCAdapter
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    c = Client.objects.create(id='test-client', name='Test Client')
    ClientMetadata.objects.create(client=c, legacy_sub=False)
    return c


# all scopes enabled returns full claims set
def test_claims(user, client):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid', 'profile', 'email'])

    # given_name and family_name are excluded for privacy
    assert 'given_name' not in claims
    assert 'family_name' not in claims

    # standard fields are mapped from the user model
    assert claims['nickname'] == user.username
    assert claims['email'] == user.email
    assert claims['email_verified'] is False
    assert claims['name'] == user.full_name


# email scope returns only email fields, not profile fields
def test_claims_email_scope_only(user, client):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid', 'email'])
    assert 'email' in claims
    assert 'email_verified' in claims
    assert 'name' not in claims
    assert 'preferred_username' not in claims


# profile scope returns only profile fields, not email
def test_claims_profile_scope_only(user, client):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid', 'profile'])
    assert 'name' in claims
    assert 'preferred_username' in claims
    assert 'nickname' in claims
    assert 'email' not in claims


# openid scope alone returns only the sub claim
def test_claims_openid_only(user, client):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid'])
    assert 'sub' in claims
    assert len(claims) == 1


# null DOB omits the birthdate key entirely rather than returning None
def test_claims_no_birthdate(user, client):
    user.date_of_birth = None
    user.save()
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid', 'profile'])
    assert 'birthdate' not in claims


# birthdate is returned in ISO 8601 format
def test_claims_with_birthdate(client):
    from datetime import date

    user = UserFactory(date_of_birth=date(2000, 6, 15))
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid', 'profile'])
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


# sub is a UUID string for non-legacy clients
def test_sub_is_uuid(user):
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    client = Client.objects.create(id='test-uuid', name='UUID App')
    ClientMetadata.objects.create(client=client, legacy_sub=False)

    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid'])
    assert claims['sub'] == str(user.uuid)
    uuid.UUID(claims['sub'])  # validates it parses as a UUID


# legacy_sub flag makes the sub return the numeric PK
def test_legacy_sub(user):
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    client = Client.objects.create(id='test-legacy', name='Legacy App')
    ClientMetadata.objects.create(client=client, legacy_sub=True)

    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=client, scopes=['openid'])
    assert claims['sub'] == str(user.pk)


# get_user_by_sub resolves UUID sub to correct user
def test_get_user_by_uuid_sub(user):
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    client = Client.objects.create(id='test-uuid-lookup', name='UUID Lookup')
    ClientMetadata.objects.create(client=client, legacy_sub=False)

    adapter = FoxtailOIDCAdapter()
    found = adapter.get_user_by_sub(client=client, sub=str(user.uuid))
    assert found == user


# get_user_by_sub resolves PK sub for legacy clients
def test_get_user_by_legacy_sub(user):
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    client = Client.objects.create(id='test-legacy-lookup', name='Legacy Lookup')
    ClientMetadata.objects.create(client=client, legacy_sub=True)

    adapter = FoxtailOIDCAdapter()
    found = adapter.get_user_by_sub(client=client, sub=str(user.pk))
    assert found == user


# get_user_by_sub returns None for invalid sub format
def test_get_user_by_sub_invalid(user):
    from allauth.idp.oidc.models import Client

    from apps.accounts.models import ClientMetadata

    client = Client.objects.create(id='test-invalid', name='Invalid Sub')
    ClientMetadata.objects.create(client=client, legacy_sub=False)

    adapter = FoxtailOIDCAdapter()
    assert adapter.get_user_by_sub(client=client, sub='not-a-uuid') is None
