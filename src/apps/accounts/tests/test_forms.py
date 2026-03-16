from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from faker import Faker
from PIL import Image

from apps.accounts.forms import SignupForm, UserForm
from apps.accounts.forms.custom import MAX_AVATAR_SIZE
from conftest import CAPTCHA_FIELD

from .factories import UserFactory


def _png_bytes(size=None):
    buf = BytesIO()
    Image.new('RGB', (1, 1)).save(buf, format='PNG')
    header = buf.getvalue()
    if size is None:
        return header
    return header + b'\x00' * (size - len(header))


fake = Faker()
pytestmark = pytest.mark.django_db


class TestSignupForm:
    """Test SignupForm username, email, and password rules."""

    # form accepts valid data with all fields populated
    def test_valid_form(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert form.is_valid()

    # reserved usernames like 'root' are rejected
    def test_banned_username(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': 'root',
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # duplicate username is rejected
    def test_duplicate_username(self, user):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': user.username,
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # duplicate email is rejected
    def test_duplicate_email(self, user):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': user.email,
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'email' in form.errors

    # malformed email address is rejected
    def test_invalid_email(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': 'chocolate',
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'email' in form.errors

    # empty email is rejected (required field)
    def test_missing_email(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': '',
                'password1': proto_user._password,
                'password2': proto_user._password,
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'email' in form.errors

    # weak passwords are rejected
    def test_poor_password(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': proto_user.email,
                'password1': 'password',
                'password2': 'password',
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'password1' in form.errors

    # mismatched password confirmation is rejected
    def test_mismatched_password(self):
        proto_user = UserFactory.build()

        form = SignupForm(
            {
                'username': proto_user.username,
                'email': proto_user.email,
                'password1': proto_user._password,
                'password2': fake.password(),
                **CAPTCHA_FIELD,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'password2' in form.errors


class TestUserForm:
    """Test UserForm username and date-of-birth rules."""

    # form accepts valid data with all fields populated
    def test_full_form(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                'username': proto_user.username,
                'date_of_birth': proto_user.date_of_birth,
                'full_name': proto_user.full_name,
            }
        )

        assert form.is_valid()

    # valid with only required fields (optional fields null)
    def test_minimal_form(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                'username': proto_user.username,
                'date_of_birth': None,
                'full_name': None,
            }
        )

        assert form.is_valid()

    # reserved usernames are rejected
    def test_banned_username(self, user):
        form = UserForm(
            {
                'username': 'root',
                'date_of_birth': None,
                'full_name': None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # duplicate username is rejected
    def test_duplicate_username(self, user):
        form = UserForm(
            {
                'username': user.username,
                'date_of_birth': None,
                'full_name': None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # special characters in username are rejected
    def test_invalid_username(self):
        form = UserForm(
            {
                'username': 'user****name',
                'date_of_birth': None,
                'full_name': None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # blank username is rejected
    def test_blank_username(self):
        form = UserForm(
            {
                'username': None,
                'date_of_birth': None,
                'full_name': None,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'username' in form.errors

    # future date of birth is rejected
    def test_future_dob(self):
        proto_user = UserFactory.build()

        form = UserForm(
            {
                'username': proto_user.username,
                'date_of_birth': fake.future_date(),
                'full_name': proto_user.full_name,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert 'date_of_birth' in form.errors

    # avatar exceeding 5 MB is rejected
    def test_avatar_oversized(self):
        avatar = SimpleUploadedFile('avatar.png', _png_bytes(MAX_AVATAR_SIZE + 1), content_type='image/png')
        proto_user = UserFactory.build()
        form = UserForm(
            {'username': proto_user.username},
            files={'avatar': avatar},
        )
        assert not form.is_valid()
        assert 'avatar' in form.errors

    # avatar exactly at 5 MB passes size check
    def test_avatar_at_limit(self):
        avatar = SimpleUploadedFile('avatar.png', _png_bytes(MAX_AVATAR_SIZE), content_type='image/png')
        proto_user = UserFactory.build()
        form = UserForm(
            {'username': proto_user.username},
            files={'avatar': avatar},
        )
        assert 'avatar' not in (form.errors or {})

    # avatar under 5 MB passes size check
    def test_avatar_under_limit(self):
        avatar = SimpleUploadedFile('avatar.png', _png_bytes(), content_type='image/png')
        proto_user = UserFactory.build()
        form = UserForm(
            {'username': proto_user.username},
            files={'avatar': avatar},
        )
        assert 'avatar' not in (form.errors or {})
