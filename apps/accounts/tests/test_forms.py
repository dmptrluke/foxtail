import pytest

from apps.accounts.forms import SignupForm

from .factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSignupForm:
    def test_valid_form(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": proto_user.email,
                "password1": proto_user._password,
                "password2": proto_user._password,
                "captcha": "N/A"
            }
        )

        assert form.is_valid()

    def test_invalid_form(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": proto_user.email,
                "password1": proto_user._password,
                "password2": 'not at all the correct password',
                "captcha": "N/A"
            }
        )

        assert not form.is_valid()
