from unittest.mock import MagicMock, patch

from django.core.mail import EmailMessage

import pytest

from apps.email.engine import AsyncEmailBackend, render_email, send_email

pytestmark = [pytest.mark.django_db]


def _make_message(**kwargs):
    defaults = {'subject': 'Test', 'body': 'body', 'to': ['a@b.com']}
    defaults.update(kwargs)
    return EmailMessage(**defaults)


class TestAsyncEmailBackend:
    # enqueuing a message returns sent count
    def test_send_messages_returns_count(self):
        backend = AsyncEmailBackend()
        with patch('apps.email.engine.send_email_message') as mock_task:
            result = backend.send_messages([_make_message(), _make_message()])
        assert result == 2
        assert mock_task.call_count == 2

    # fail_silently=False propagates enqueue errors
    def test_send_messages_raises_on_enqueue_failure(self):
        backend = AsyncEmailBackend(fail_silently=False)
        with patch('apps.email.engine.send_email_message', side_effect=ConnectionError), pytest.raises(ConnectionError):
            backend.send_messages([_make_message()])

    # fail_silently=True swallows enqueue errors and logs them
    def test_send_messages_silent_logs_enqueue_failure(self, caplog):
        backend = AsyncEmailBackend(fail_silently=True)
        with patch('apps.email.engine.send_email_message', side_effect=ConnectionError):
            result = backend.send_messages([_make_message()])
        assert result == 0
        assert 'Failed to enqueue email' in caplog.text

    # partial failure: counts only successfully enqueued messages
    def test_send_messages_partial_failure(self):
        backend = AsyncEmailBackend(fail_silently=True)
        with patch('apps.email.engine.send_email_message', side_effect=[None, ConnectionError]):
            result = backend.send_messages([_make_message(), _make_message()])
        assert result == 1


class TestRenderEmail:
    TEMPLATE = 'emails/contact/submission'
    CONTEXT = {
        'name': 'Fox',
        'authentication': False,
        'email': 'fox@example.com',
        'message': 'Hello',
        'SITE_URL': 'https://example.com',
    }

    # produces multipart message with text and HTML alternatives
    def test_renders_text_and_html(self):
        msg = render_email('Subject', ['to@b.com'], self.TEMPLATE, self.CONTEXT)
        assert msg.body
        assert len(msg.alternatives) == 1
        html, mime = msg.alternatives[0]
        assert mime == 'text/html'
        assert '<html' in html.lower()

    # MJML tags are compiled away — raw <mjml> should not appear in output
    def test_mjml_compiled_to_html(self):
        msg = render_email('Subject', ['to@b.com'], self.TEMPLATE, self.CONTEXT)
        html = msg.alternatives[0][0]
        assert '<mjml>' not in html
        assert '<mj-' not in html

    # template context variables are interpolated in both text and HTML
    def test_context_interpolated(self):
        msg = render_email('Subject', ['to@b.com'], self.TEMPLATE, self.CONTEXT)
        assert 'Fox' in msg.body
        html = msg.alternatives[0][0]
        assert 'Fox' in html

    # subject, to, and from_email are passed through correctly
    def test_message_fields(self):
        msg = render_email('My Subject', ['to@b.com'], self.TEMPLATE, self.CONTEXT, from_email='from@b.com')
        assert msg.subject == 'My Subject'
        assert msg.to == ['to@b.com']
        assert msg.from_email == 'from@b.com'

    # custom headers are applied to the message
    def test_custom_headers(self):
        msg = render_email('S', ['to@b.com'], self.TEMPLATE, self.CONTEXT, headers={'X-Custom': 'value'})
        assert msg.extra_headers['X-Custom'] == 'value'


class TestSendEmail:
    TEMPLATE = 'emails/contact/submission'
    CONTEXT = {
        'name': 'Fox',
        'authentication': False,
        'email': 'fox@example.com',
        'message': 'Hello',
        'SITE_URL': 'https://example.com',
    }

    # send_email renders and sends via the configured backend
    def test_send_email_sends(self, mailoutbox):
        send_email('Subject', ['to@b.com'], self.TEMPLATE, self.CONTEXT)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].subject == 'Subject'


class TestSendEmailMessageTask:
    # logs when backend throws (huey catches the re-raise for retries)
    def test_logs_on_backend_exception(self, caplog):
        from apps.email.tasks import send_email_message

        msg = _make_message()
        mock_conn = MagicMock()
        mock_conn.send_messages.side_effect = ConnectionError('smtp down')
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('apps.email.tasks.get_connection', return_value=mock_conn):
            send_email_message(msg)
        assert 'Failed to send email' in caplog.text

    # logs when backend returns 0 (silent failure)
    def test_logs_on_zero_sent(self, caplog):
        from apps.email.tasks import send_email_message

        msg = _make_message()
        mock_conn = MagicMock()
        mock_conn.send_messages.return_value = 0
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)

        with patch('apps.email.tasks.get_connection', return_value=mock_conn):
            send_email_message(msg)
        assert 'returned failure' in caplog.text


class TestTemplateRendering:
    # contact submission template renders with all context fields
    def test_contact_submission_template(self):
        context = {
            'name': 'TestFox',
            'authentication': 'testuser',
            'email': 'fox@example.com',
            'message': 'Test message body',
            'SITE_URL': 'https://example.com',
        }
        msg = render_email('Contact', ['to@b.com'], 'emails/contact/submission', context)
        assert 'TestFox' in msg.body
        assert 'testuser' in msg.body
        assert 'Test message body' in msg.body

    # email confirmation template renders with allauth context
    def test_email_confirmation_template(self, user):
        site = MagicMock()
        site.name = 'furry.nz'
        context = {
            'user': user,
            'current_site': site,
            'activate_url': 'https://example.com/confirm/abc123',
        }
        msg = render_email('Confirm', ['to@b.com'], 'emails/account/email_confirmation', context)
        assert user.username in msg.body
        assert 'https://example.com/confirm/abc123' in msg.body
        html = msg.alternatives[0][0]
        assert 'https://example.com/confirm/abc123' in html

    # password reset template renders with reset URL and username
    def test_password_reset_template(self):
        context = {
            'password_reset_url': 'https://example.com/reset/xyz',
            'username': 'foxuser',
        }
        msg = render_email('Reset', ['to@b.com'], 'emails/account/password_reset_key', context)
        assert 'https://example.com/reset/xyz' in msg.body
        assert 'foxuser' in msg.body
        html = msg.alternatives[0][0]
        assert 'https://example.com/reset/xyz' in html
