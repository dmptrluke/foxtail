from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from django import forms


class ContactForm(forms.Form):
    captcha = ReCaptchaField()
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False

        self.fields['captcha'].label = False

        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('email', css_class='col-md-6')
            ),
            Row(
                Column('message', css_class='col-md-12'),
            ),
            Row(
                Column('captcha', css_class='col-md-12'),
            )
        )
