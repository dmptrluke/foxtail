from django.conf import settings

import pytest

from apps.core.models import SiteSettings
from apps.email.rendering import build_message, mjml_template_exists, send_email

pytestmark = pytest.mark.django_db

PREFIX = 'contact/email/submission'
CONTEXT = {
    'name': 'Fox',
    'authentication': 'testuser',
    'email': 'fox@example.com',
    'message': 'Hello & welcome',
}


class TestBuildMessage:
    # produces a multipart message with text body, subject and compiled HTML
    def test_text_subject_and_html(self):
        msg = build_message(PREFIX, ['to@b.com'], CONTEXT)
        assert msg.subject == 'Contact form submission - Fox'
        assert 'Hello & welcome' in msg.body
        assert 'testuser' in msg.body
        html, mimetype = msg.alternatives[0]
        assert mimetype == 'text/html'
        assert 'Hello &amp; welcome' in html

    # MJML tags are compiled away
    def test_mjml_compiled_to_html(self):
        html = build_message(PREFIX, ['to@b.com'], CONTEXT).alternatives[0][0]
        assert '<mjml>' not in html
        assert '<mj-' not in html

    # the header logo is an absolute URL built from SITE_URL and the static tag
    def test_logo_uses_site_url(self):
        html = build_message(PREFIX, ['to@b.com'], CONTEXT).alternatives[0][0]
        assert f'{settings.SITE_URL}/static/images/paw-96.png' in html

    # rendering always uses site settings while leaving caller-provided context untouched
    def test_renderer_owns_conf_without_mutating_context(self):
        context = {**CONTEXT, 'conf': {'org_name': 'Caller override'}}
        msg = build_message(PREFIX, ['to@b.com'], context)
        html = msg.alternatives[0][0]
        assert SiteSettings.get_solo().org_name in html
        assert 'Caller override' not in html
        assert context['conf'] == {'org_name': 'Caller override'}

    # caller-provided context wins over the defaults
    def test_context_overrides_defaults(self):
        msg = build_message(PREFIX, ['to@b.com'], {**CONTEXT, 'SITE_URL': 'https://other.example'})
        assert 'https://other.example/static/images/paw-96.png' in msg.alternatives[0][0]

    # from_email and headers are applied to the message
    def test_from_email_and_headers(self):
        msg = build_message(PREFIX, ['to@b.com'], CONTEXT, from_email='from@b.com', headers={'X-Custom': 'value'})
        assert msg.from_email == 'from@b.com'
        assert msg.extra_headers['X-Custom'] == 'value'


class TestSendEmail:
    # send_email renders and sends via the configured backend
    def test_send_email_sends(self, mailoutbox):
        send_email(PREFIX, ['to@b.com'], CONTEXT)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].subject == 'Contact form submission - Fox'


class TestMjmlTemplateExists:
    # true for emails that ship an .mjml template
    def test_existing(self):
        assert mjml_template_exists(PREFIX)

    # false for emails that don't, so callers can fall back
    def test_missing(self):
        assert not mjml_template_exists('account/email/does_not_exist')
