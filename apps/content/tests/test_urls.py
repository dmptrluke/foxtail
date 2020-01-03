from django.urls import resolve, reverse


def test_index():
    assert reverse("content:index") == "/"
    assert resolve("/").view_name == "content:index"


def test_page():
    assert reverse("content:page", kwargs={"slug": "randompage"}) == "/randompage/"
    assert resolve("/randompage/").view_name == "content:page"
