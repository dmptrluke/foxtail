from django.conf import settings
from django.forms import CharField, EmailField, Form, Textarea

from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from apps.core.mixins import HoneypotFormMixin


class ContactForm(HoneypotFormMixin, CSPFormMixin, Form):
    if settings.RECAPTCHA_INVISIBLE:
        captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    else:
        captcha = ReCaptchaField()

    name = CharField(required=True)
    email = EmailField(required=True)
    message = CharField(required=True, widget=Textarea)
