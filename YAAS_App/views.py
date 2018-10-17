from django.shortcuts import render, redirect
from YAAS_App.forms import *
from Auctions.models import Auction
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import os
# Create your views here.


def search(request):
    query = request.GET.get('q')
    results = Auction.objects.filter(Q(title__icontains=query), deadline__gte=timezone.now(),
                                     status=Auction.STATUS_ACTIVE)
    return render(request, "index.html", {"auctions": results})


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.session['next_url']
                if next_url:
                    return redirect(next_url)
                return redirect("index")
            else:
                print("INVALID LOGIN")

    else:
        form = LoginForm()
        request.session['next_url'] = request.GET.get('next')

    context = {"form": form}
    return render(request, "registration/login.html", context)


def index(request):
    auctions = Auction.objects.all().filter(deadline__gte=timezone.now(), status=Auction.STATUS_ACTIVE)
    return render(request, "index.html", {'auctions': auctions})


@login_required()
def my_account(request):
    my_auctions = Auction.objects.filter(seller=request.user)
    return render(request, "my_account.html", {"my_auctions": my_auctions})


@login_required()
def change_email_done(request):
    return render(request, "email_change_done.html")


@login_required()
def change_email(request):
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


@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    email_path = settings.EMAIL_FILE_PATH
    email_list = os.listdir(email_path)
    banned_auctions = Auction.objects.filter(status=Auction.STATUS_BANNED)
    return render(request, "admin_panel.html", {'emails': email_list, 'banned': banned_auctions})

