from urllib.parse import parse_qs, urlparse

from django.urls import reverse

import pytest

pytestmark = pytest.mark.django_db


class TestAdminLogin:
    url = reverse('admin:login')

    # unauthenticated requests redirect to allauth login with ?next pointing to admin
    def test_unauthenticated_redirects_to_allauth_login(self, client):
        response = client.get(self.url)

        assert response.status_code == 302
        parsed = urlparse(response.url)
        assert parsed.path == reverse('account_login')
        assert parse_qs(parsed.query)['next'] == [reverse('admin:index')]

    # authenticated staff users skip login and go straight to admin index
    def test_authenticated_staff_redirects_to_admin_index(self, client, user):
        user.is_staff = True
        user.save()
        client.force_login(user)

        response = client.get(self.url)

        assert response.status_code == 302
        assert response.url == reverse('admin:index')

    # non-staff users are redirected to allauth login even if authenticated
    def test_non_staff_redirects_to_allauth_login(self, client, user):
        client.force_login(user)

        response = client.get(self.url)

        assert response.status_code == 302
        parsed = urlparse(response.url)
        assert parsed.path == reverse('account_login')
