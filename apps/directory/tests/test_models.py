import pytest

pytestmark = pytest.mark.django_db


class TestProfile:
    def test_string_representation(self, profile):
        assert str(profile) == profile.profile_URL
