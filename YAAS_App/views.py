from django.shortcuts import render, redirect
from YAAS_App.forms import *
from Auctions.models import Auction, Bid
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import translation
from django.contrib.auth.decorators import user_passes_test
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import AuctionSerializer
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
import os
import json
from .models import *
from Auctions.views import send_email
from faker import Faker
from random import *
import datetime
from django.utils.translation import ugettext_lazy as _
from concurrency.exceptions import RecordModifiedError
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
                set_user_lang(request, user)
                next_url = request.session['next_url']
                if next_url:
                    return redirect(next_url)
                return redirect("index")
            else:
                print("INVALID LOGIN")
                messages.error(request, _("Invalid login information!"))

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


def set_language(request, lang):
    locale = "en"  # Default is english
    if lang == UserLanguage.LANG_SV:
        locale = "sv"

    if request.user.is_authenticated:
        try:
            user_lang = UserLanguage.objects.get(user=request.user)
            user_lang.lang_pref = lang
            user_lang.save()
            messages.info(request, _("Your language setting has been updated!"))

        except UserLanguage.DoesNotExist:
            user_lang = UserLanguage.objects.create(user=request.user, lang_pref=lang)
            user_lang.save()
            messages.info(request, _("Your language setting has been saved!"))

    translation.activate(locale)
    request.session[translation.LANGUAGE_SESSION_KEY] = locale
    print(request.session[translation.LANGUAGE_SESSION_KEY])
    return index(request)


def set_user_lang(request, user):
    locale = "en"
    try:
        user_lang = UserLanguage.objects.get(user=user)
        if user_lang.lang_pref == 2:
            locale = "sv"
    except UserLanguage.DoesNotExist:
        user_lang = UserLanguage.objects.create(user=user)
        user_lang.save()
    translation.activate(locale)
    request.session[translation.LANGUAGE_SESSION_KEY] = locale


  # API STUFF


def api_about(request):
    return render(request, "api_about.html")


@api_view(['GET'])
def auction_list(request, format=None):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query is not None:
            auctions = Auction.objects.filter(Q(title__icontains=query), deadline__gte=timezone.now(),
                                              status=Auction.STATUS_ACTIVE)
        else:
            auctions = Auction.objects.filter(deadline__gte=timezone.now(),
                                              status=Auction.STATUS_ACTIVE)
        serializer = AuctionSerializer(auctions, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def auction_detail(request, pk, format=None):
    try:
        auction = Auction.objects.get(pk=pk)
    except AuctionSerializer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AuctionSerializer(auction, context={'request': request})
        request.session['description1'] = auction.description
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            if auction.status == Auction.STATUS_ACTIVE:
                if auction.seller != request.user:
                    if auction.description == request.session.get('description1', "nothing"):
                        curr_bid = auction.winning_bid
                        curr_amount = 0.00
                        compare = 0
                        if curr_bid is not None:
                            curr_amount = curr_bid.amount
                            compare = curr_bid.bidder
                        if compare != request.user:
                            data = request.body
                            try:
                                json_r = json.loads(data.decode('utf-8'))
                            except json.decoder.JSONDecodeError:
                                json_r = {}
                            if 'bid' not in json_r:
                                return Response(data={"detail": "You have to specify your bid in the json format using "
                                                                "'bid' (use double quotes) as key and the value in "
                                                                "decimal or integer form "
                                                                "(no quotes)"})
                            new_bid = json_r['bid']
                            if type(new_bid) == int or type(new_bid) == float:
                                new_bid = new_bid*100
                                new_bid = int(new_bid)  # Chop of extra decimals
                                new_bid = new_bid/100.0
                                if new_bid >= auction.min_price and new_bid > curr_amount:
                                    bid = Bid(bidder=request.user, auction=auction, amount=new_bid)
                                    bid.save()
                                    auction.winning_bid = bid
                                    try:
                                        auction.save()
                                        send_email(auction.title + ": New bid",
                                                   bid.bidder.__str__() + " has placed a new bid of "
                                                   + str(bid.amount) + "€ on your auction '" + auction.title + "'!",
                                                   [auction.seller.email])
                                        if curr_bid is not None:
                                            send_email(auction.title + ": New bid",
                                                       "You have been overbid on the auction '" + auction.title + "'!",
                                                       [curr_bid.bidder.email])
                                        return Response(data={"detail": "Bid made successfully!"})
                                    except RecordModifiedError:
                                        return Response(data={"detail": "Someone else bid before you. GET the page to "
                                                                        "view the new bid and try bidding again!"})
                                else:
                                    return Response(data={"detail": "Your bid has to be greater than the minimum price and "
                                                                    "the current bid!"})

                            else:
                                return Response(data={"detail": "Your bid amount has to be specified in decimal or "
                                                                "integer form!"})
                        else:
                            return Response(data={"detail": "You are already winning this auction!"})
                    else:
                        return Response(data={"detail": "The description seems to have changed. Please GET the specific"
                                                        "auction again before retrying."})
                else:
                    return Response(data={"detail": "You cannot bid on your own auction!"})
            else:
                return Response(data={"detail": "This auction is no longer active."})
        return Response(data={"detail": "YOU HAVE TO BE LOGGED IN TO MAKE BIDS."})  # API Returns similar error


@user_passes_test(lambda u: u.is_superuser)
def generate_data(request):  # Data generation program
    random_products = ['Computer', 'Raspberry Pi', 'iPhone', 'Television', 'Jam', 'Xbox', 'Playstation', 'Homework']
    desc = "Very good product for sale. This product will make your life 200% better."
    fake = Faker()
    print("---Starting data generation program----\nGenerating 50 random users and one auction each")
    n = 2
    for _ in range(0, 50):
        profile = fake.simple_profile()
        user = User.objects.create_user(username=profile['username'], email=profile['mail'], password=fake.password())
        user.first_name = profile['name'].split()[0]
        user.last_name = profile['name'].split()[1]
        user.save()
        auction = Auction(seller=user, title=sample(random_products, 1)[0], description=desc,
                          min_price=round(uniform(10, 500)),
                          deadline=timezone.now()+datetime.timedelta(hours=(72+randint(0, 50))))
        auction.save()
        print(str(n)+"% done")
        n = n+2
    print("Generating complete.\nGenerating 50 random bids by random users on random auctions")
    n = 2
    for i in range(0, 50):
        random_auction = sample(list(Auction.objects.all()), 1)[0]
        random_user = sample(list(User.objects.all()), 1)[0]

        winning_bid = 0
        winner = 0
        if random_auction.winning_bid is not None:
            winning_bid = random_auction.winning_bid.amount
            winner = random_auction.winning_bid.bidder
        if random_user != random_auction.seller and random_user != winner:
            if winning_bid == 0:
                bid_amount = random_auction.min_price + round(uniform(1, 10))
            else:
                bid_amount = winning_bid + round(uniform(1, 10))
            bid = Bid(bidder=random_user, amount=bid_amount, auction=random_auction)
            bid.save()
            random_auction.winning_bid = bid
            random_auction.save()
            print(str(n) + "% done")
            n = n + 2
    messages.info(request, "Data Generation done! Click on Home to see the results :)")
    return render(request, "index.html")


# REMOVE THIS
def delete_all(self):
    print(len(Auction.objects.all().ge))
    return redirect("index")
