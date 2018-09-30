from django.shortcuts import render, redirect
from YAAS_App.forms import UserRegistrationForm, ChangeEmailForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
# Create your views here.


def index(request):
    return render(request, "index.html")


def my_account(request):
    if request.user.is_authenticated:
        return render(request, "my_account.html")
    return redirect("login")


def change_email_done(request):
    if request.user.is_authenticated:
        return render(request, "email_change_done.html")
    return redirect("login")


def change_email(request):
    if request.user.is_authenticated:
        context = {}
        if request.method == "POST":
            form = ChangeEmailForm(request.POST)
            if form.is_valid():
                new_email1 = form.cleaned_data["new_email1"]
                new_email2 = form.cleaned_data["new_email2"]
                if new_email1 == new_email2:
                    try:
                        User.objects.get(email=new_email1)
                        context["email_exists"] = True
                    except User.DoesNotExist:
                        username = request.user.username
                        user = User.objects.get(username=username)
                        user.email = new_email1
                        user.save()
                        return redirect("email_change_done")
                else:
                    context["emails_no_match"] = True
        else:
            form = ChangeEmailForm()
        context["form"] = form
        return render(request, "email_change_form.html", context)
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("index")

    else:
        form = UserRegistrationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


