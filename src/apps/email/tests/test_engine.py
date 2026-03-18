import pytest

from apps.email.engine import render_email

pytestmark = pytest.mark.django_db


class TestRenderEmail:
    # render_email injects SiteSettings as 'conf' when not provided by caller
    def test_conf_injected_into_context(self):
        context = {
            'password_reset_url': 'https://example.com/reset/',
            'username': 'testuser',
        }
        msg = render_email(
            subject='Test',
            to=['test@example.com'],
            template='emails/account/password_reset_key',
            context=context,
        )
        assert 'conf' in context
        assert msg.body  # text body rendered without error
        assert msg.alternatives  # HTML alternative attached
