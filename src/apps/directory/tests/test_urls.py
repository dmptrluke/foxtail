from django.urls import resolve, reverse


def test_profile():
    assert reverse("directory:profile", kwargs={"slug": "kakapo"}) == "/directory/kakapo/"
    assert resolve("/directory/kakapo/").view_name == "directory:profile"


def test_profile_edit():
    assert reverse("directory:profile_edit", kwargs={"slug": "kakapo"}) == "/directory/kakapo/edit/"
    assert resolve("/directory/kakapo/edit/").view_name == "directory:profile_edit"


def test_profile_create():
    assert reverse("directory:profile_create") == "/directory/create/"
    assert resolve("/directory/create/").view_name == "directory:profile_create"


def test_character():
    assert reverse("directory:character", kwargs={"slug": "kakapo", "pk": 1}) == "/directory/kakapo/1/"
    assert resolve("/directory/kakapo/1/").view_name == "directory:character"


def test_character_edit():
    assert reverse("directory:character_edit", kwargs={"slug": "kakapo", "pk": 1}) == "/directory/kakapo/1/edit/"
    assert resolve("/directory/kakapo/1/edit/").view_name == "directory:character_edit"
