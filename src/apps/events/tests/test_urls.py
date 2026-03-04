from django.urls import resolve, reverse


def test_list():
    assert reverse("events:list") == "/events/"
    assert resolve("/events/").view_name == "events:list"


def test_list_year():
    assert reverse("events:list_year", kwargs={"year": 2019}) == "/events/2019/"
    assert resolve("/events/2019/").view_name == "events:list_year"


def test_detail():
    assert reverse("events:detail", kwargs={"year": 2019, "slug": "test"}) == "/events/2019/test/"
    assert resolve("/events/2019/test/").view_name == "events:detail"
