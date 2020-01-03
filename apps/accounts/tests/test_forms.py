import pytest
from faker import Faker

from apps.accounts.forms import SignupForm

from .factories import UserFactory

fake = Faker()
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
            }
        )

        assert form.is_valid()

    def test_duplicate_username(self, user):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": user.username,
                "email": proto_user.email,
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

    def test_duplicate_email(self, user):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": user.email,
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors

    def test_invalid_email(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": 'chocolate',
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors

    def test_missing_email(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": "",
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors

    def test_poor_password(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": proto_user.email,
                "password1": 'password',
                "password2": 'password',
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "password1" in form.errors

    def test_mismatched_password(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": proto_user.username,
                "email": proto_user.email,
                "password1": proto_user._password,
                "password2": fake.password(),
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "password2" in form.errors
