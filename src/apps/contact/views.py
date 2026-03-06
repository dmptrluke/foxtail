import logging

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from csp_helpers.mixins import CSPViewMixin
from mail_templated_simple import send_mail

from .forms import ContactForm

logger = logging.getLogger(__name__)


class ContactView(CSPViewMixin, FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.GET.get('email', None)
        return initial

    def _fake_success(self):
        messages.success(self.request, 'Your message has been sent.')
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        if form.cleaned_data.get('website'):
            logger.warning(
                'Honeypot triggered on contact form from %s',
                self.request.META.get('REMOTE_ADDR', 'unknown'),
            )
            return self._fake_success()

        context = {
            'name': form.cleaned_data['name'],
            'authentication': False,
            'email': form.cleaned_data['email'],
            'message': form.cleaned_data['message'],
            'SITE_URL': settings.SITE_URL,
        }
        if self.request.user.is_authenticated:
            context['authentication'] = self.request.user.username

        send_mail('contact/emails/submission.tpl', context, None, settings.CONTACT_EMAILS)

        messages.success(self.request, 'Your message has been sent.')
        return super().form_valid(form)


__all__ = ['ContactView']
