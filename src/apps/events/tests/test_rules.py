import pytest

from ..rules import is_editor

pytestmark = pytest.mark.django_db


class TestIsEditor:
    # moderator group member is an editor
    def test_moderator_is_editor(self, editor):
        assert is_editor(editor)

    # staff user is an editor
    def test_staff_is_editor(self, staff_user):
        assert is_editor(staff_user)

    # regular user is not an editor
    def test_regular_user_not_editor(self, user):
        assert not is_editor(user)
