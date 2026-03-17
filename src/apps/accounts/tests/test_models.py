from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.utils.timezone import localdate

import pytest
from allauth.account.models import EmailAddress
from allauth.idp.oidc.models import Client as OIDCClient

from apps.accounts.models import ClientMetadata

pytestmark = pytest.mark.django_db


# __str__ returns the user's username
def test_string_representation(user):
    assert str(user) == user.username


# get_full_name() returns full_name, not first/last name
def test_get_full_name(user):
    assert user.get_full_name() == user.full_name


# get_short_name() returns username
def test_get_short_name(user):
    assert user.get_short_name() == user.username


class TestUserClean:
    """Test User.clean() date-of-birth validation."""

    # future DOB raises ValidationError
    def test_rejects_future_dob(self, user):
        user.date_of_birth = localdate() + timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            user.clean()
        assert 'date_of_birth' in exc_info.value.message_dict

    # today's date is also rejected (strict past-only boundary)
    def test_rejects_today_dob(self, user):
        user.date_of_birth = localdate()
        with pytest.raises(ValidationError) as exc_info:
            user.clean()
        assert 'date_of_birth' in exc_info.value.message_dict

    # past dates are accepted without error
    def test_accepts_past_dob(self, user):
        user.date_of_birth = date(2000, 1, 1)
        user.clean()

    # null DOB is allowed (field is optional)
    def test_accepts_null_dob(self, user):
        user.date_of_birth = None
        user.clean()


class TestUserEmailVerified:
    """Test the email_verified property against allauth email state."""

    # verified primary email returns True (feeds into OIDC email_verified claim)
    def test_verified_true(self, user):
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        assert user.email_verified is True

    # unverified primary email returns False (OIDC consumers rely on this)
    def test_verified_false_unverified(self, user):
        EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
        assert user.email_verified is False

    # no EmailAddress rows defaults to unverified
    def test_verified_false_no_email(self, user):
        assert user.email_verified is False


class TestClientMetadata:
    """Test the ClientMetadata model attached to OIDC clients."""

    # __str__ displays the associated OIDC client name
    def test_str(self):
        oidc_client = OIDCClient.objects.create(name='Test App')
        metadata = ClientMetadata.objects.create(client=oidc_client)
        assert str(metadata) == 'Metadata for Test App'
