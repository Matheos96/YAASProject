from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class MyUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="First name:", max_length=150, required=True)
    last_name = forms.CharField(label="Last name", max_length=150, required=True)
    email = forms.EmailField(label="Email adress:", required=True)
    username = forms.CharField(label="Username:", required=True)
    password1 = forms.CharField(label="Password:", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Repeat password:", widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

