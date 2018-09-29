from django.shortcuts import render, redirect
from YAAS_App.forms import MyUserCreationForm
from django.contrib.auth import authenticate, login
# Create your views here.


def index(request):
    return render(request, "index.html")


def register(request):
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("index")

    else:
        form = MyUserCreationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


