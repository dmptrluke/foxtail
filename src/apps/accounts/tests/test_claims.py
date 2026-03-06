import pytest

from apps.accounts.adapter import FoxtailOIDCAdapter

pytestmark = pytest.mark.django_db


def test_claims(user):
    adapter = FoxtailOIDCAdapter()
    claims = adapter.get_claims('userinfo', user, client=None, scopes=['openid', 'profile', 'email'])

    # given_name and family_name should NOT be present
    assert 'given_name' not in claims
    assert 'family_name' not in claims

    # test provided data
    assert claims['nickname'] == user.username
    assert claims['email'] == user.email
    assert claims['email_verified'] is False

    # test other data
    assert claims['name'] == user.full_name
