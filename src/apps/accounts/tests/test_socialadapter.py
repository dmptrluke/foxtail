from django.contrib.auth import get_user_model

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
