from django.contrib.auth import get_user_model
from django.forms import ModelForm, SelectDateWidget


class UserForm(ModelForm):
    class Meta:
        model = get_user_model()
        widgets = {
            'date_of_birth': SelectDateWidget(years=range(1920, 2011),
                                              empty_label=("Year", "Month", "Day")),
        }
        fields = ('username', 'date_of_birth', 'full_name')


__all__ = ['UserForm']
