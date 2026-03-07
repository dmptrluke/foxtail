from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ImageField, ModelForm, SelectDateWidget

from apps.core.widgets import CroppedImageWidget

MAX_AVATAR_SIZE = 5 * 1024 * 1024


class UserForm(ModelForm):
    avatar = ImageField(required=False, widget=CroppedImageWidget(aspect_ratio=1))

    class Meta:
        model = get_user_model()
        widgets = {
            'date_of_birth': SelectDateWidget(years=range(1920, 2011), empty_label=('Year', 'Month', 'Day')),
        }
        fields = ('username', 'date_of_birth', 'full_name', 'avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar or not hasattr(avatar, 'size'):
            return avatar

        if avatar.size > MAX_AVATAR_SIZE:
            raise ValidationError('Avatar must be smaller than 5 MB.')

        return avatar


__all__ = ['UserForm']
