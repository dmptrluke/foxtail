from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UnauthenticatedResponseCodeTests(TestCase):
    def test_profile(self):
        url = reverse('account_profile')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}', 302)

    def test_password(self):
        url = reverse('account_change_password')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}', 302)

        url = reverse('account_set_password')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}', 302)

    def test_email(self):
        url = reverse('account_email')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}', 302)

    def test_connections(self):
        url = reverse('socialaccount_connections')
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}', 302)

    def test_logout(self):
        url = reverse('account_logout')
        response = self.client.get(url)
        self.assertRedirects(response, '/', 302)


class AuthenticatedResponseCodeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('user1', 'user1@example.com')
        self.user_with_password = get_user_model().objects.create_user('user2', 'user2@example.com', 'placeholder')

    def test_profile(self):
        self.client.force_login(self.user)

        url = reverse('account_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_email(self):
        self.client.force_login(self.user)

        url = reverse('account_email')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_connections(self):
        self.client.force_login(self.user)

        url = reverse('socialaccount_connections')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_set_password(self):
        self.client.force_login(self.user)

        url = reverse('account_set_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_password(self):
        self.client.force_login(self.user_with_password)

        url = reverse('account_change_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_to_set(self):
        """ user has no password set, so this should redirect to set_password """
        self.client.force_login(self.user)

        url = reverse('account_change_password')
        redirect_url = reverse('account_set_password')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, 302)

    def test_set_to_change(self):
        """ user has a password set, so this should redirect to change_password """
        self.client.force_login(self.user_with_password)

        url = reverse('account_set_password')
        redirect_url = reverse('account_change_password')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, 302)
