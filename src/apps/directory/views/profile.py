from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView

from csp_helpers.mixins import CSPViewMixin
from rules.contrib.views import AutoPermissionRequiredMixin

from ..forms import ProfileCreateForm, ProfileForm
from ..models import Profile


class ProfileView(DetailView):
    queryset = Profile.objects.all().select_related('user')
    slug_field = 'profile_URL'


class ProfileEditView(AutoPermissionRequiredMixin, CSPViewMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Profile
    success_message = 'Your profile has been updated'
    slug_field = 'profile_URL'
    template_name = 'directory/profile_edit.html'
    form_class = ProfileForm


class ProfileCreateView(CSPViewMixin, SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Profile
    success_message = 'Your profile has been updated'
    slug_field = 'profile_URL'
    template_name = 'directory/profile_create.html'
    form_class = ProfileCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        if self.model.objects.filter(user=self.request.user).exists():
            return redirect(self.request.user.profile.get_modify_url())
        else:
            return super().get(*args, **kwargs)


__all__ = ["ProfileView", "ProfileEditView", "ProfileCreateView"]
