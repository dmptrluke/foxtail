from django.conf import settings
from django.forms import Form

from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class SocialLinkRedirectForm(CSPFormMixin, Form):
    if settings.RECAPTCHA_INVISIBLE:
        captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    else:
        captcha = ReCaptchaField()
