from django.urls import resolve, reverse


# account_profile resolves to /accounts/
def test_profile():
    assert reverse('account_profile') == '/accounts/'
    assert resolve('/accounts/').view_name == 'account_profile'


# account_signup resolves to /accounts/signup/
def test_signup():
    assert reverse('account_signup') == '/accounts/signup/'
    assert resolve('/accounts/signup/').view_name == 'account_signup'


# account_reset_password resolves to /accounts/password/reset/
def test_reset_password():
    assert reverse('account_reset_password') == '/accounts/password/reset/'
    assert resolve('/accounts/password/reset/').view_name == 'account_reset_password'


# account_application_list resolves to /accounts/applications/
def test_application_list():
    assert reverse('account_application_list') == '/accounts/applications/'
    assert resolve('/accounts/applications/').view_name == 'account_application_list'


# account_settings resolves to /accounts/settings/
def test_settings():
    assert reverse('account_settings') == '/accounts/settings/'
    assert resolve('/accounts/settings/').view_name == 'account_settings'


# account_application_revoke resolves with pk parameter
def test_application_revoke():
    assert reverse('account_application_revoke', kwargs={'pk': 1}) == '/accounts/applications/1/revoke/'
    assert resolve('/accounts/applications/1/revoke/').view_name == 'account_application_revoke'


# mfa_authenticate resolves to /accounts/2fa/authenticate/
def test_mfa_authenticate():
    assert reverse('mfa_authenticate') == '/accounts/2fa/authenticate/'
    assert resolve('/accounts/2fa/authenticate/').view_name == 'mfa_authenticate'
