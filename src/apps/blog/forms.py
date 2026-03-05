from django.conf import settings
from django.forms import ModelForm, Textarea

from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from .models import Comment

RECAPTCHA_ENABLED = getattr(settings, 'RECAPTCHA_ENABLED', True)
RECAPTCHA_INVISIBLE = getattr(settings, 'RECAPTCHA_INVISIBLE', False)


class CommentForm(CSPFormMixin, ModelForm):
    if RECAPTCHA_ENABLED:
        if RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
            captcha = ReCaptchaField()

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'rows': 4})
        }
