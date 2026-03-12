from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

import pytest

from apps.accounts.admin import CustomUserAdmin
from apps.accounts.models import User, Verification

pytestmark = pytest.mark.django_db


class TestCustomUserAdmin:
    def setup_method(self):
        self.admin = CustomUserAdmin(User, AdminSite())
        self.factory = RequestFactory()

    # verified badge shows True when user has a verification record
    def test_is_verified_display_true(self, user, second_user):
        Verification.objects.create(user=user, verified_by=second_user)
        user.refresh_from_db()
        assert self.admin.is_verified_display(user) is True

    # verified badge shows False when user has no verification record
    def test_is_verified_display_false(self, user):
        assert self.admin.is_verified_display(user) is False

    # queryset prefetches verification to avoid N+1 on list view
    def test_get_queryset_select_related(self, user):
        request = self.factory.get('/admin/accounts/user/')
        request.user = user
        qs = self.admin.get_queryset(request)
        assert 'verification' in qs.query.select_related


class TestAccountsAdminPages:
    # user changelist loads for staff users
    def test_user_changelist(self, client, user):
        user.is_staff = True
        user.is_superuser = True
        user.save()
        client.force_login(user)

        response = client.get('/admin/accounts/user/')

        assert response.status_code == 200

    # user change page loads with verification inline
    def test_user_change_page(self, client, user):
        user.is_staff = True
        user.is_superuser = True
        user.save()
        client.force_login(user)

        response = client.get(f'/admin/accounts/user/{user.pk}/change/')

        assert response.status_code == 200
        assert b'Verification' in response.content
