from django.test import Client
from django.urls import reverse

import pytest
from formguard.test import GuardedFormTestMixin

from .factories import SocialLinkFactory

pytestmark = pytest.mark.django_db


class TestSocialLinkRedirectAuthenticated:
    # logged-in user gets immediate 302 to the real URL
    def test_authenticated_redirects(self, client, user):
        link = SocialLinkFactory(url='https://t.me/+test123')
        client.force_login(user)
        response = client.get(reverse('social_link_redirect', args=[link.pk]))
        assert response.status_code == 302
        assert response['Location'] == 'https://t.me/+test123'

    # redirect increments click_count
    def test_authenticated_increments_click_count(self, client, user):
        link = SocialLinkFactory()
        client.force_login(user)
        client.get(reverse('social_link_redirect', args=[link.pk]))
        link.refresh_from_db()
        assert link.click_count == 1


class TestSocialLinkRedirectAnonymous(GuardedFormTestMixin):
    # anonymous user sees the interstitial page
    def test_anonymous_gets_interstitial(self, client):
        link = SocialLinkFactory()
        response = client.get(reverse('social_link_redirect', args=[link.pk]))
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'link' in response.context

    # valid POST with guard data redirects to real URL
    def test_valid_post_redirects(self, client):
        link = SocialLinkFactory(url='https://discord.gg/test')
        response = client.post(reverse('social_link_redirect', args=[link.pk]), self.guard_data())
        assert response.status_code == 302
        assert response['Location'] == 'https://discord.gg/test'

    # valid POST increments click_count
    def test_valid_post_increments_click_count(self, client):
        link = SocialLinkFactory()
        client.post(reverse('social_link_redirect', args=[link.pk]), self.guard_data())
        link.refresh_from_db()
        assert link.click_count == 1

    # POST without guard data re-renders form with errors
    def test_invalid_post_rerenders(self, client):
        link = SocialLinkFactory()
        response = client.post(reverse('social_link_redirect', args=[link.pk]), {})
        assert response.status_code == 200
        assert response.context['form'].errors

    # POST without CSRF token succeeds (view is csrf_exempt for in-app browser compatibility)
    def test_post_without_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        link = SocialLinkFactory(url='https://discord.gg/test')
        response = csrf_client.post(reverse('social_link_redirect', args=[link.pk]), self.guard_data())
        assert response.status_code == 302


class TestSocialLinkRedirect404:
    # nonexistent PK returns 404
    def test_get_nonexistent(self, client):
        response = client.get(reverse('social_link_redirect', args=[99999]))
        assert response.status_code == 404

    # POST to nonexistent PK returns 404
    def test_post_nonexistent(self, client):
        response = client.post(reverse('social_link_redirect', args=[99999]), {})
        assert response.status_code == 404
