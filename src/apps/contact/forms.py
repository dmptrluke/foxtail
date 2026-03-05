from django.conf import settings
from django.forms import CharField, EmailField, Form, Textarea

from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

RECAPTCHA_ENABLED = getattr(settings, 'RECAPTCHA_ENABLED', True)
RECAPTCHA_INVISIBLE = getattr(settings, 'RECAPTCHA_INVISIBLE', False)


class ContactForm(CSPFormMixin, Form):
    if RECAPTCHA_ENABLED:
        if RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
            captcha = ReCaptchaField()

    name = CharField(required=True)
    email = EmailField(required=True)
    website = CharField(required=False)
    message = CharField(
        required=True,
        widget=Textarea
    )
