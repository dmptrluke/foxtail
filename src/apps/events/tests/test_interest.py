from django.urls import reverse

import pytest

from apps.events.models import EventInterest


@pytest.mark.django_db
class TestEventInterestToggle:
    """POST /events/<pk>/interest/ toggles interest for authenticated users."""

    def test_toggle_on(self, client, user, event):
        # Creates an interest record when none exists and returns interested=True with count=1
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 200
        data = response.json()
        assert data['interested'] is True
        assert data['count'] == 1
        assert EventInterest.objects.filter(event=event, user=user).exists()

    def test_toggle_off(self, client, user, event):
        # Deletes an existing interest record and returns interested=False with count=0
        client.force_login(user)
        EventInterest.objects.create(event=event, user=user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        data = response.json()
        assert data['interested'] is False
        assert data['count'] == 0

    def test_anonymous_forbidden(self, client, event):
        # Rejects unauthenticated POST requests with 403
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 403

    def test_get_not_allowed(self, client, user, event):
        # Rejects GET requests with 405
        client.force_login(user)
        response = client.get(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 405
