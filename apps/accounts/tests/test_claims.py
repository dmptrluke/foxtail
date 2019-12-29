from copy import deepcopy
from dataclasses import dataclass
from datetime import date

from oidc_provider.lib.claims import STANDARD_CLAIMS

from ..claims import userinfo


@dataclass
class FakeUser:
    username: str
    email: str
    email_verified: bool = True
    full_name: str = None
    gender: str = None
    date_of_birth: date = None


def test_minimal():
    user = FakeUser('userone', 'test@example.com')
    claims = userinfo(deepcopy(STANDARD_CLAIMS), user)

    # test overridden defaults
    assert claims['given_name'] is None
    assert claims['family_name'] is None

    # test provided data
    assert claims['nickname'] == 'userone'
    assert claims['email'] == 'test@example.com'
    assert claims['email_verified'] is True

    # test other data
    assert claims['name'] is None
