from django.urls import resolve, reverse


def test_profile():
    assert reverse("account_profile") == "/accounts/"
    assert resolve("/accounts/").view_name == "account_profile"


def test_signup():
    assert reverse("account_signup") == "/accounts/signup/"
    assert resolve("/accounts/signup/").view_name == "account_signup"


def test_reset_password():
    assert reverse("account_reset_password") == "/accounts/password/reset/"
    assert resolve("/accounts/password/reset/").view_name == "account_reset_password"
