from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="First name", max_length=150, required=True)
    last_name = forms.CharField(label="Last name", max_length=150, required=True)
    email = forms.EmailField(label="Email address", required=True)
    username = forms.CharField(label="Username", required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = "post"
        self.helper.layout = Layout("first_name",
                                    "last_name",
                                    "email",
                                    "username",
                                    "password1",
                                    "password2",
                                    Submit("submit", "Register", css_class="btn btn-primary"))

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
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


class ChangeEmailForm(forms.Form):
    new_email1 = forms.EmailField(label="New Email address", required=True)
    new_email2 = forms.EmailField(label="New Email address again", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper
        self.helper.form_method = "post"
        self.helper.layout = Layout("new_email1",
                                    "new_email2",
                                    Submit("submit", "Change", css_class="btn btn-primary"))

