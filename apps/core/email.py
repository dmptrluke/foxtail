"""
Based on code from <https://github.com/pmclanahan/django-celery-email>

License for the derived code follows:
    Copyright (c) 2010, Paul McLanahan
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

      * Redistributions of source code must retain the above copyright notice, this
        list of conditions and the following disclaimer.
      * Redistributions in binary form must reproduce the above copyright notice,
        this list of conditions and the following disclaimer in the documentation
        and/or other materials provided with the distribution.
      * Neither the name of Paul McLanahan nor the names of any contributors may be
        used to endorse or promote products derived from this software without
        specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

import django_rq


def send_messages_async(messages, **kwargs):
    logger = logging.getLogger(__name__)

    conn = get_connection(backend=settings.EMAIL_REAL_BACKEND, **kwargs)
    try:
        conn.open()
    except Exception:
        logger.exception("Cannot reach email backend %s", settings.EMAIL_REAL_BACKEND)

    messages_sent = 0

    for message in messages:
        try:
            sent = conn.send_messages([message])
            if sent is not None:
                messages_sent += sent
            logger.info("Successfully sent email message to %r.", message.to)
        except Exception as e:
            # Not expecting any specific kind of exception here because it
            # could be any number of things, depending on the backend
            # TODO: We need to handle this properly.
            logger.exception("Failed to send email message to %r (%r)",
                             message.to, e)

    conn.close()
    return messages_sent


class AsyncEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, messages, **kwargs):
        django_rq.enqueue(send_messages_async, messages, **kwargs)
