from copy import deepcopy

import pytest
from oidc_provider.lib.claims import STANDARD_CLAIMS

from ..claims import userinfo

pytestmark = pytest.mark.django_db


def test_claims(user):
    claims = userinfo(deepcopy(STANDARD_CLAIMS), user)

    # test overridden defaults
    assert claims['given_name'] is None
    assert claims['family_name'] is None

    # test provided data
    assert claims['nickname'] == user.username
    assert claims['email'] == user.email
    assert claims['email_verified'] is False

    # test other data
    assert claims['name'] is user.full_name
