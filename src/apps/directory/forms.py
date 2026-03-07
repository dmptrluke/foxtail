from django.forms import ModelForm

from cjswidget.widgets import CJSWidget

from .models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = (
            'profile_URL',
            'description',
            'description_privacy',
            'country',
            'region',
            'location_privacy',
            'age_privacy',
            'birthday_privacy',
        )

        widgets = {
            'country': CJSWidget(options={'shouldSort': False}),
            'region': CJSWidget(options={'shouldSort': False}),
        }


class ProfileCreateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_URL',)
