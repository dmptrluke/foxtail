from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import UpdateView

from apps.accounts.forms import UserForm


class UserView(LoginRequiredMixin, UpdateView):
    template_name = 'profile.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')


__all__ = ['UserView']
