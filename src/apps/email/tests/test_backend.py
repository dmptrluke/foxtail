from unittest.mock import MagicMock, patch

from django.core.mail import EmailMessage

import pytest

from apps.email.backend import AsyncEmailBackend
from apps.email.tasks import send_email_message


def _make_message(**kwargs):
    defaults = {'subject': 'Test', 'body': 'body', 'to': ['a@b.com']}
    defaults.update(kwargs)
    return EmailMessage(**defaults)


class TestAsyncEmailBackend:
    # the backend counts successfully enqueued messages
    def test_send_messages_returns_count(self):
        backend = AsyncEmailBackend()
        with patch('apps.email.backend.send_email_message') as mock_task:
            result = backend.send_messages([_make_message(), _make_message()])
        assert result == 2
        assert mock_task.call_count == 2

    # fail_silently=False propagates enqueue errors
    def test_send_messages_raises_on_enqueue_failure(self):
        backend = AsyncEmailBackend(fail_silently=False)
        with (
            patch('apps.email.backend.send_email_message', side_effect=ConnectionError),
            pytest.raises(ConnectionError),
        ):
            backend.send_messages([_make_message()])

    # fail_silently=True swallows enqueue errors and logs them
    def test_send_messages_silent_logs_enqueue_failure(self, caplog):
        backend = AsyncEmailBackend(fail_silently=True)
        with patch('apps.email.backend.send_email_message', side_effect=ConnectionError):
            result = backend.send_messages([_make_message()])
        assert result == 0
        assert 'Failed to enqueue email' in caplog.text

    # partial failure: counts only successfully enqueued messages
    def test_send_messages_partial_failure(self):
        backend = AsyncEmailBackend(fail_silently=True)
        with patch('apps.email.backend.send_email_message', side_effect=[None, ConnectionError]):
            result = backend.send_messages([_make_message(), _make_message()])
        assert result == 1


class TestSendEmailMessageTask:
    @staticmethod
    def _connection(**send_kwargs):
        conn = MagicMock()
        conn.send_messages.configure_mock(**send_kwargs)
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        return conn

    # delivery exceptions are logged
    def test_logs_on_backend_exception(self, caplog):
        conn = self._connection(side_effect=ConnectionError('smtp down'))
        with patch('apps.email.tasks.get_connection', return_value=conn):
            send_email_message(_make_message())
        assert 'Failed to send email' in caplog.text

    # zero deliveries are logged as failures
    def test_logs_on_zero_sent(self, caplog):
        conn = self._connection(return_value=0)
        with patch('apps.email.tasks.get_connection', return_value=conn):
            send_email_message(_make_message())
        assert 'returned failure' in caplog.text
