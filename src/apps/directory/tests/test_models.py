import pytest

from apps.directory.models import Profile

pytestmark = pytest.mark.django_db


class TestProfile:
    def test_string_representation(self, profile: Profile):
        assert str(profile) == profile.profile_URL

    def test_get_absolute_url(self, profile: Profile):
        assert profile.get_absolute_url() == f"/directory/{profile.profile_URL}/"

    def test_get_modify_url(self, profile: Profile):
        assert profile.get_modify_url() == f"/directory/{profile.profile_URL}/edit/"

    def test_structured_data(self, profile: Profile):
        structured_data = profile.structured_data
        assert structured_data['@type'] == 'Person'
        assert structured_data['name'] == profile.user.username
