import pytest
from faker import Faker

from apps.accounts.forms import SignupForm, UserForm

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

    def test_banned_username(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                "username": "root",
                "email": proto_user.email,
                "password1": proto_user._password,
                "password2": proto_user._password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

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


class TestUserForm:
    def test_full_form(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                "username": proto_user.username,
                "date_of_birth": proto_user.date_of_birth,
                "full_name": proto_user.full_name,
            }
        )

        assert form.is_valid()

    def test_minimal_form(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                "username": proto_user.username,
                "date_of_birth": None,
                "full_name": None,
            }
        )

        assert form.is_valid()

    def test_banned_username(self, user):
        form = UserForm(
            {
                "username": "root",
                "date_of_birth": None,
                "full_name": None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

    def test_duplicate_username(self, user):
        form = UserForm(
            {
                "username": user.username,
                "date_of_birth": None,
                "full_name": None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

    def test_invalid_username(self):
        form = UserForm(
            {
                "username": "user****name",
                "date_of_birth": None,
                "full_name": None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

    def test_blank_username(self):
        form = UserForm(
            {
                "username": None,
                "date_of_birth": None,
                "full_name": None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "username" in form.errors

    def test_future_dob(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                "username": proto_user.username,
                "date_of_birth": fake.future_date(),
                "full_name": proto_user.full_name,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "date_of_birth" in form.errors
