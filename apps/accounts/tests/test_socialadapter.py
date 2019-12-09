from django.contrib.auth import get_user_model

from datetime import datetime

from apps.accounts.authentication import SocialAccountAdapter
test_adapter = SocialAccountAdapter()


class FakeSocialLogin:
    def __init__(self, user):
        self.user = user


def test_minimal():
    """ test if populate_user works with the minimum set of data """
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com'
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'


def test_full():
    """ test if populate_user works with the maximum set of data """
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'name': 'Test Face',
        'birthdate': '2006-05-23',
        'gender': 'male'
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == "Test Face"

    assert processed_user.date_of_birth.year == 2006
    assert processed_user.date_of_birth.month == 5
    assert processed_user.date_of_birth.day == 23


def test_split_names():
    """ test if populate_user works with split names """
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'first_name': 'Test',
        'last_name': 'Face',
        'gender': 'male'
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == "Test Face"


def test_both_names():
    """ test if populate_user works with both kinds of name """
    user = get_user_model()()
    login = FakeSocialLogin(user)

    data = {
        'username': 'testface',
        'email': 'testface@example.com',
        'name': 'John Doe',
        'first_name': 'Test',
        'last_name': 'Face',
        'gender': 'male'
    }

    processed_user = test_adapter.populate_user(None, login, data)

    assert processed_user.username == 'testface'
    assert processed_user.full_name == "John Doe"
