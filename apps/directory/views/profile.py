from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import Http404
from django.views.generic import DetailView, UpdateView

from csp_helpers.mixins import CSPViewMixin

from ..forms import ProfileForm
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


__all__ = ["ProfileView", "ProfileEditView"]
