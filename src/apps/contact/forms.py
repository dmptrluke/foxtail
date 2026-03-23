from django.forms import CharField, EmailField, Form, Textarea

from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class ContactForm(GuardedFormMixin, CSPFormMixin, Form):
    name = CharField(required=True)
    email = EmailField(required=True)
    message = CharField(required=True, widget=Textarea)
