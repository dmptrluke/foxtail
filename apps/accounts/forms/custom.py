from django.contrib.auth import get_user_model
from django.forms import ModelForm, SelectDateWidget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Fieldset, Layout, Row, Submit


class UserForm(ModelForm):
    class Meta:
        model = get_user_model()
        widgets = {
            'date_of_birth': SelectDateWidget(years=range(1920, 2011),
                                              empty_label=("Year", "Month", "Day")),
        }
        fields = ('username', 'date_of_birth', 'full_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                Row(
                    Column('username', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Personal Information',
                HTML('<p class="small">This information is optional, and may be requested by'
                     ' third-party applications. It will not be shared without your explicit consent.</p>'),
                Row(
                    Column(Field('full_name', autocomplete='name'), css_class='col-md-6'),
                ),
                Row(
                    Column('date_of_birth', css_class='col-md-6'),
                )
            ),
            Submit('submit', 'Save Changes'),
        )


__all__ = ['UserForm']
