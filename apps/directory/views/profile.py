from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, UpdateView

from csp_helpers.mixins import CSPViewMixin

from ..forms import ProfileCreateForm, ProfileForm
from ..models import Profile


class ProfileView(DetailView):
    queryset = Profile.objects.all().select_related('user')
    slug_field = 'profile_URL'

    def get_context_data(self, **kwargs):
        kwargs['can_modify'] = self.object.can_modify(self.request.user)
        return super().get_context_data(**kwargs)


class ProfileEditView(CSPViewMixin, SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Profile
    success_message = 'Your profile has been updated'
    slug_field = 'profile_URL'
    form_class = ProfileForm

    def get_object(self, *args, **kwargs):
        profile = super().get_object(*args, **kwargs)
        if not profile.can_modify(self.request.user):
            raise Http404
        return profile


class ProfileCreateView(CSPViewMixin, SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Profile
    success_message = 'Your profile has been updated'
    slug_field = 'profile_URL'
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
