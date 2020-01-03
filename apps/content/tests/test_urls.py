from django.urls import resolve, reverse


def test_index():
    assert reverse("index") == "/"
    assert resolve("/").view_name == "index"


def test_page():
    assert reverse("page-detail", kwargs={"slug": "randompage"}) == "/randompage/"
    assert resolve("/randompage/").view_name == "page-detail"
