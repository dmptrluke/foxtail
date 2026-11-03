from django.test import RequestFactory

import pytest
from allauth.core.context import request_context

from apps.accounts.authentication import AccountAdapter

pytestmark = pytest.mark.django_db


def _render_mail(prefix, to, context):
    with request_context(RequestFactory().get('/')):
        return AccountAdapter().render_mail(prefix, to, context)


class TestRenderMail:
    # email confirmation renders text and MJML-compiled HTML with the site subject prefix
    def test_email_confirmation(self, user):
        context = {'user': user, 'activate_url': 'https://example.com/confirm/abc123'}
        msg = _render_mail('account/email/email_confirmation', 'to@b.com', context)
        assert msg.to == ['to@b.com']
        assert msg.subject.startswith('[')
        assert 'Confirm your' in msg.subject
        assert user.username in msg.body
        assert 'https://example.com/confirm/abc123' in msg.body
        assert 'https://example.com/confirm/abc123' in msg.alternatives[0][0]

    # password reset renders reset URL and username
    def test_password_reset(self):
        context = {'password_reset_url': 'https://example.com/reset/xyz', 'username': 'foxuser'}
        msg = _render_mail('account/email/password_reset_key', 'to@b.com', context)
        assert 'Reset your' in msg.subject
        assert 'https://example.com/reset/xyz' in msg.body
        assert 'foxuser' in msg.body
        assert 'https://example.com/reset/xyz' in msg.alternatives[0][0]

    # emails without an MJML template fall back to allauth's own rendering
    def test_unconverted_email_falls_back_to_allauth(self, user):
        context = {'user': user, 'email': 'to@b.com', 'password_changed': True}
        msg = _render_mail('account/email/password_changed', 'to@b.com', context)
        assert msg.to == ['to@b.com']
        assert not getattr(msg, 'alternatives', [])
