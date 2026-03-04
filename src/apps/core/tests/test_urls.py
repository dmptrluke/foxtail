from django.urls import resolve, reverse


def test_robots():
    assert reverse("robots") == "/robots.txt"
    assert resolve("/robots.txt").view_name == "robots"
