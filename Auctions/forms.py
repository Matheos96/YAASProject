from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class LoginForm(forms.ModelForm):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_action = reverse("login_user")
        self.helper.form_method = "post"
        self.helper.layout = Layout("username",
                                    "password",
                                    Submit("login", "Login", css_class="btn btn-success"))



