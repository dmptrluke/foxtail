import pytest

pytestmark = pytest.mark.django_db


def test_string_representation(user):
    assert str(user) == user.username


def test_get_full_name(user):
    assert user.get_full_name() == user.full_name


def test_get_short_name(user):
    assert user.get_short_name() == user.username
