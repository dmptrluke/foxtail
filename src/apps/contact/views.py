from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from csp_helpers.mixins import CSPViewMixin

from apps.core.mixins import HoneypotViewMixin
from apps.email.engine import send_email

from .forms import ContactForm


class ContactView(HoneypotViewMixin, CSPViewMixin, FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')

    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.request.GET.get('email', None)
        return initial

    def form_valid(self, form):
        if self.is_honeypot(form):
            return self.honeypot_success()

        name = form.cleaned_data['name']
        context = {
            'name': name,
            'authentication': False,
            'email': form.cleaned_data['email'],
            'message': form.cleaned_data['message'],
            'SITE_URL': settings.SITE_URL,
        }
        if self.request.user.is_authenticated:
            context['authentication'] = self.request.user.username

        send_email(
            subject=f'Contact form submission - {name}',
            to=settings.CONTACT_EMAILS,
            template='emails/contact/submission',
            context=context,
        )

        messages.success(self.request, 'Your message has been sent.')
        return super().form_valid(form)


__all__ = ['ContactView']
