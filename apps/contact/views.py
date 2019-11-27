from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from mail_templated_simple import send_mail

from .forms import ContactForm


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            context = {
                'name': name,
                'email': email,
                'message': message,
                'SITE_URL': settings.SITE_URL
            }
            send_mail('emails/submission.tpl', context, None, ['website@furry.nz'])

            messages.success(request, 'Your message has been sent.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
