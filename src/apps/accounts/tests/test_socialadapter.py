from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model

import pytest

from apps.accounts.authentication import SocialAccountAdapter, valid_email_or_none

test_adapter = SocialAccountAdapter()


class FakeSocialLogin:
    def __init__(self, user):
        self.user = user


# maps username and email from minimal OAuth data
def test_minimal():
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {'username': 'testface', 'email': 'testface@example.com'}

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'


# maps all fields including parsed birthdate from full OAuth data
def test_full():
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'name': 'Test Face',
        'birthdate': '2006-05-23',
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == 'Test Face'

    assert processed_user.date_of_birth.year == 2006
    assert processed_user.date_of_birth.month == 5
    assert processed_user.date_of_birth.day == 23


# first_name + last_name are merged into full_name
def test_split_names():
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'first_name': 'Test',
        'last_name': 'Face',
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == 'Test Face'


# name field takes precedence over first_name + last_name
def test_both_names():
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'name': 'John Doe',
        'first_name': 'Test',
        'last_name': 'Face',
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == 'John Doe'


# malformed birthdate is silently ignored rather than crashing signup
def test_invalid_birthdate_ignored():
    user = get_user_model()()
    login = FakeSocialLogin(user)
    data = {'username': 'testface', 'email': 'test@example.com', 'birthdate': 'not-a-date'}
    processed_user = test_adapter.populate_user(None, login, data)
    assert processed_user.date_of_birth is None


# empty OAuth data defaults to empty strings
def test_empty_data():
    user = get_user_model()()
    login = FakeSocialLogin(user)
    processed_user = test_adapter.populate_user(None, login, {})
    assert processed_user.username == ''
    assert processed_user.email == ''


class TestValidEmailOrNone:
    """Test valid_email_or_none email filtering."""

    # valid email address passes through unchanged
    def test_valid_email(self):
        assert valid_email_or_none('user@example.com') == 'user@example.com'

    # invalid email format returns None
    def test_invalid_email(self):
        assert valid_email_or_none('not-an-email') is None

    # empty string returns None
    def test_empty_string(self):
        assert valid_email_or_none('') is None

    # None input returns None
    def test_none(self):
        assert valid_email_or_none(None) is None


def _make_sociallogin(provider, uid, is_existing=False):
    account = Mock()
    account.provider = provider
    account.uid = uid
    account.extra_data = {}
    sociallogin = Mock()
    sociallogin.account = account
    sociallogin.is_existing = is_existing
    return sociallogin


@pytest.mark.django_db
class TestPreSocialLogin:
    # bot-linked user doing OAuth gets auto-connected
    def test_auto_connects_telegram_link(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        sociallogin = _make_sociallogin('telegram', '12345')
        request = Mock(user=user)
        test_adapter.pre_social_login(request, sociallogin)
        sociallogin.connect.assert_called_once_with(request, user)

    # no TelegramLink passes through silently
    def test_no_link_passes(self):
        sociallogin = _make_sociallogin('telegram', '99999')
        request = Mock()
        test_adapter.pre_social_login(request, sociallogin)
        sociallogin.connect.assert_not_called()

    # non-telegram provider is ignored
    def test_non_telegram_ignored(self):
        sociallogin = _make_sociallogin('github', '12345')
        request = Mock()
        test_adapter.pre_social_login(request, sociallogin)
        sociallogin.connect.assert_not_called()

    # already-existing social account is ignored
    def test_existing_ignored(self, user, telegram_link_factory):
        telegram_link_factory(user=user, telegram_id=12345)
        sociallogin = _make_sociallogin('telegram', '12345', is_existing=True)
        request = Mock()
        test_adapter.pre_social_login(request, sociallogin)
        sociallogin.connect.assert_not_called()

    # exception is caught and logged, OAuth continues
    def test_exception_caught(self):
        sociallogin = _make_sociallogin('telegram', '12345')
        request = Mock()
        with patch(
            'apps.telegram.models.TelegramLink.objects.select_related',
            side_effect=RuntimeError('db down'),
        ):
            test_adapter.pre_social_login(request, sociallogin)
        # should not raise
