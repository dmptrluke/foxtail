from django.urls import resolve, reverse


def test_profile():
    assert reverse("directory:profile", kwargs={"slug": "kakapo"}) == "/directory/kakapo/"
    assert resolve("/directory/kakapo/").view_name == "directory:profile"


def test_profile_edit():
    assert reverse("directory:profile_edit", kwargs={"slug": "kakapo"}) == "/directory/edit/kakapo/"
    assert resolve("/directory/edit/kakapo/").view_name == "directory:profile_edit"


def test_character():
    assert reverse("directory:character", kwargs={"slug": "kakapo", "pk": 1}) == "/directory/kakapo/1/"
    assert resolve("/directory/kakapo/1/").view_name == "directory:character"


def test_character_edit():
    assert reverse("directory:character_edit", kwargs={"slug": "kakapo", "pk": 1}) == "/directory/edit/kakapo/1/"
    assert resolve("/directory/edit/kakapo/1/").view_name == "directory:character_edit"
