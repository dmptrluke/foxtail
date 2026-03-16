from django.urls import reverse

import pytest

from apps.events.models import EventInterest


@pytest.mark.django_db
class TestEventInterestToggle:
    """Test event interest toggle endpoint."""

    # posting with status=interested creates interest
    def test_set_interested(self, client, user, event):
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}), {'status': 'interested'})
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'interested'
        assert data['interested_count'] == 1
        assert data['going_count'] == 0
        assert EventInterest.objects.filter(event=event, user=user, status='interested').exists()

    # posting with status=going creates going record
    def test_set_going(self, client, user, event):
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}), {'status': 'going'})
        data = response.json()
        assert data['status'] == 'going'
        assert data['interested_count'] == 0
        assert data['going_count'] == 1

    # posting with status=going upgrades from interested
    def test_upgrade_interested_to_going(self, client, user, event):
        client.force_login(user)
        EventInterest.objects.create(event=event, user=user, status='interested')
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}), {'status': 'going'})
        data = response.json()
        assert data['status'] == 'going'
        assert EventInterest.objects.get(event=event, user=user).status == 'going'

    # posting without status removes interest
    def test_remove_interest(self, client, user, event):
        client.force_login(user)
        EventInterest.objects.create(event=event, user=user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        data = response.json()
        assert data['status'] is None
        assert data['interested_count'] == 0
        assert not EventInterest.objects.filter(event=event, user=user).exists()

    # posting with invalid status returns 400
    def test_invalid_status(self, client, user, event):
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}), {'status': 'maybe'})
        assert response.status_code == 400

    # anonymous users are rejected with 403
    def test_anonymous_forbidden(self, client, event):
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 403

    # GET returns 405
    def test_get_not_allowed(self, client, user, event):
        client.force_login(user)
        response = client.get(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 405

    # counts reflect multiple users with different statuses
    def test_mixed_status_counts(self, client, user, second_user, event):
        EventInterest.objects.create(event=event, user=second_user, status='interested')
        EventInterest.objects.create(event=event, user=user, status='going')
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}), {'status': 'going'})
        data = response.json()
        assert data['interested_count'] == 1
        assert data['going_count'] == 1

    # unpublished events return 404
    def test_unpublished_event_returns_404(self, client, user, event):
        event.publish_status = 0  # NEVER_AVAILABLE
        event.save()
        client.force_login(user)
        response = client.post(reverse('events:interest', kwargs={'pk': event.pk}))
        assert response.status_code == 404
