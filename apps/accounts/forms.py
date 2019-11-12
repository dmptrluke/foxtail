from allauth.account import forms as auth_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field
from django.forms import SelectDateWidget, ModelForm

from apps.accounts.models import User
from apps.core.fields import CustomCheckbox


class SignupForm(auth_forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        self.fields['username'].help_text = "Required. 150 characters or fewer."
        self.fields['email'].help_text = "Required. This must be a valid email address for account activation."

        self.helper.layout = Layout(
            Row(
                Column(Field('username', placeholder=''), css_class='col-md-6'),
                Column(Field('email', placeholder=''), css_class='col-md-6')
            ),
            Row(
                Column(Field('password1', placeholder=''), css_class='col-md-6'),
                Column(Field('password2', placeholder=''), css_class='col-md-6')
            )
        )


class LoginForm(auth_forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            'login',
            'password',
            CustomCheckbox('remember')
        )


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'date_of_birth', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False

        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('date_of_birth', css_class='col-md-6'),
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            )
        )

