import django_rq
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend


def send_messages_async(messages, **kwargs):
    conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
    try:
        conn.open()
    except Exception:
        pass

    messages_sent = 0

    for message in messages:
        try:
            sent = conn.send_messages([message])
            if sent is not None:
                messages_sent += sent
            print("Successfully sent email message to %r.", message.to)
        except Exception as e:
            # Not expecting any specific kind of exception here because it
            # could be any number of things, depending on the backend
            print("Failed to send email message to {}. ({})".format(message.to, e))

    conn.close()
    return messages_sent


class AsyncEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(AsyncEmailBackend, self).__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, messages, **kwargs):
        django_rq.enqueue(send_messages_async, messages, **kwargs)
