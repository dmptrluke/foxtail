from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ImageField, ModelForm, SelectDateWidget

from apps.images.widgets import CroppedImageWidget


class UserForm(ModelForm):
    avatar = ImageField(required=False, widget=CroppedImageWidget(aspect_ratio=1, preview_round=True))

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

        if avatar.size > settings.MAX_IMAGE_FILE_SIZE:
            mb = settings.MAX_IMAGE_FILE_SIZE / (1024 * 1024)
            raise ValidationError(f'Avatar must be smaller than {mb:.0f} MB.')

        return avatar


__all__ = ['UserForm']
