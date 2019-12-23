from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView, UpdateView

from ..forms import ProfileForm
from ..models import Profile


class ProfileView(DetailView):
    queryset = Profile.objects.all().select_related('user')
    slug_field = 'profile_URL'


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Profile
    success_message = 'Your profile has been updated'
    slug_field = 'profile_URL'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile


__all__ = ["ProfileView", "ProfileEditView"]
