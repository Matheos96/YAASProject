from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db.models import Max
from django.core import mail
from django.views import View
import datetime
from django.contrib.auth.decorators import user_passes_test
import json
import urllib.request
from django.utils.translation import ugettext_lazy as _
# Create your views here.


@method_decorator(login_required, name='dispatch')
class AddAuction(View):
    def get(self, request):
        form = AuctionForm()
        return render(request, "new_auction.html", {"form": form})

    def post(self, request):
        form = AuctionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            title = cd['title']
            desc = cd['description']
            min_price = cd['min_price']
            deadline = cd['deadline']
            if (deadline >= (timezone.now() + timedelta(hours=72))) and (min_price >= 0):
                conform = ConfirmForm(initial={"title": title, "description": desc, "min_price": min_price,
                                               "deadline": deadline})
                return render(request, "confirm_form.html", {"form": conform})

            else:
                if deadline < (timezone.now() + timedelta(hours=72)):
                    messages.add_message(request, messages.ERROR,
                                         _("The deadline has to be at least 72 hours in the future!"))
                if min_price < 0:
                    messages.add_message(request, messages.ERROR,
                                         _("The minimum price has to be at least 0!"))
        return render(request, "new_auction.html", {"form": form})


def confirm_form(request):
    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if request.POST.get("yes"):
            if form.is_valid():
                cd = form.cleaned_data
                title = cd['title']
                desc = cd['description']
                min_price = cd['min_price']
                deadline = cd['deadline']
                deadline_dt = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S%z")
                if (deadline_dt >= (timezone.now() + timedelta(hours=72))) and (float(min_price) >= 0):  # Check that the values are still valid
                    auction = Auction(title=title, description=desc, min_price=min_price, deadline=deadline)
                    auction.seller = request.user
                    auction.save()
                    to_email = [request.user.email]
                    subject = "Auction " + title + " created!"
                    message = "Your auction " + title + " has been successfully created on the YAAS Web Application!"
                    send_email(subject, message, to_email)
                else:
                    form = AuctionForm(initial={'title': title, 'description': desc, 'min_price': min_price,
                                                'deadline': deadline})
                    if deadline_dt < (timezone.now() + timedelta(hours=72)):
                        messages.error(request, _("The deadline has to be at least 72 hours in the future!"))
                    if float(min_price) < 0:
                        messages.error(request, _("The minimum price has to be at least 0!"))
                    return render(request, "new_auction.html", {"form": form})
    return redirect("index")


def send_email(subject, message, to_email):
    from_email = "YAASAuctionSite@noreply.com"
    with mail.get_connection() as connection:
        mail.EmailMessage(subject, message, from_email, to_email, connection=connection).send(fail_silently=False)
        print("mail sent")


class AuctionView(View):
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            bid_form = MakeBidForm()
            bid_form.helper.form_action = reverse("auction_view", kwargs={'auction_id': auction_id})
            request.session['description1'] = auction.description
            current_bid = get_max_bid(auction)
            bid_other_currencies = {'USD': '$0.00', 'GBP': '£0.00', 'CAD': 'CA$0.00'}
            min_other_currencies = {'USD': '$0.00', 'GBP': '£0.00', 'CAD': 'CA$0.00'}
            if auction.min_price>0:
                min_other_currencies = calc_currencies(auction.min_price)
            if current_bid is not None:
                bid_other_currencies = calc_currencies(current_bid.amount)
            return render(request, "auction.html", {'auction': auction, 'bid_form': bid_form, "max_bid": current_bid,
                                                    'bid_other_currencies': bid_other_currencies,
                                                    'min_other_currencies': min_other_currencies})
        except Auction.DoesNotExist:
            messages.warning(request, _("There is no auction with that id!"))
            return redirect("index")

    def post(self, request, auction_id):
        bid_form = MakeBidForm(request.POST)
        auction = Auction.objects.get(id=auction_id)
        current_winner = get_current_winner(auction)
        curr_bid = get_max_bid(auction)
        if auction.status == Auction.STATUS_ACTIVE:
            if request.session['description1'] == auction.description:
                if auction.seller != request.user:
                    if current_winner != request.user:
                        if bid_form.is_valid():
                            new_bid = bid_form.cleaned_data['bid']
                            if curr_bid is None:
                                cmp = auction.min_price
                            else:
                                cmp = curr_bid.amount
                            if ((new_bid > cmp) and curr_bid is not None) or ((new_bid >= cmp) and
                                                                              cmp == auction.min_price and new_bid > 0):
                                bid = Bid(bidder=request.user, auction=auction, amount=new_bid)
                                bid.save()
                                auction.winning_bid = bid
                                auction.save()
                                send_email(auction.title+": New bid", bid.bidder.__str__() + " has placed a new bid of "
                                           + str(bid.amount) + "€ on your auction '"+auction.title + "'!",
                                           [auction.seller.email])
                                if current_winner is not None:
                                    send_email(auction.title + ": New bid",
                                               "You have been overbid on the auction '" + auction.title + "'!",
                                               [current_winner.email])
                                curr_bid = bid
                                bid_form = MakeBidForm()
                                bid_form.helper.form_action = reverse("auction_view", kwargs={'auction_id': auction_id})
                            else:
                                if cmp == auction.min_price:
                                    messages.warning(request, _("Your bid has to be greater than or equal to the "
                                                                "minimum price AND greater than zero!"))
                                else:
                                    messages.warning(request, _("Your bid has to be greater than the currently winning "
                                                                "bid!"))
                    else:
                        messages.warning(request, _("You already have the highest bid!"))
                else:
                    messages.warning(request, _("You cannot bid on your own auctions!"))
            else:
                messages.error(request, _("The description seems to have changed. Please reload the page "
                                          "and try to submit your bid again. "))
        else:
            messages.warning(request, _("This auction is no longer active!"))
        bid_other_currencies = {'USD': '$0.00', 'GBP': '£0.00', 'CAD': 'CA$0.00'}
        min_other_currencies = {'USD': '$0.00', 'GBP': '£0.00', 'CAD': 'CA$0.00'}
        if auction.min_price > 0:
            min_other_currencies = calc_currencies(auction.min_price)
        if curr_bid is not None:
            bid_other_currencies = calc_currencies(curr_bid.amount)
        return render(request, "auction.html", {'auction': auction, 'bid_form': bid_form, "max_bid": curr_bid,
                                                "bid_other_currencies": bid_other_currencies,
                                                "min_other_currencies": min_other_currencies})


@method_decorator(login_required, name='dispatch')
class EditAuction(View):
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            if request.user == auction.seller:
                if auction.status == Auction.STATUS_ACTIVE:
                    form = EditAuctionForm(instance=auction)
                    return render(request, "edit_auction.html", {"form": form})
                else:
                    messages.warning(request, _("You cannot edit this auction because it is no longer active!"))
            else:
                messages.warning(request, _("You are not allowed to edit this auction!"))
        except Auction.DoesNotExist:
            messages.warning(request, _("There is no auction with that id!"))
        return redirect("index")

    def post(self, request, auction_id):
        auction = Auction.objects.get(id=auction_id)
        if auction is not None:
            if auction.status == Auction.STATUS_ACTIVE:
                auction.description = request.POST['description']
                auction.save()
                return redirect("auction_view", auction_id=auction_id)
            else:
                messages.warning(request, _("This auction is no longer active!"))
        else:
            messages.warning(request, _("There is no auction with that id!"))
        return redirect("index")


@user_passes_test(lambda u: u.is_superuser)
def ban_auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    if auction is not None:
        auction.status = Auction.STATUS_BANNED
        auction.save()
        emails = list(Bid.objects.filter(auction=auction).values_list('bidder__email', flat=True).distinct())
        emails.append([auction.seller.email])
        send_email("Auction: " + auction.title + "has been banned!", "We would like to let you know that the "
                                                                    "auction " + auction.title + "has been banned from "
                                                                                                 "the YAAS site.",
                   emails)
        messages.warning(request, _("Auction banned!"))
        return render(request, "auction.html", {'auction': auction})
    messages.warning(request, _("There is no auction with that id!"))
    return redirect("index")


def get_max_bid(auction):
    current_max_bid = Bid.objects.filter(auction=auction).aggregate(Max('amount')).get('amount__max')
    if current_max_bid is not None:
        return Bid.objects.filter(auction=auction, amount=current_max_bid).first()  # Get the object
    return None


def get_current_winner(auction):
    current_max_bid = Bid.objects.filter(auction=auction).aggregate(Max('amount')).get('amount__max')
    if current_max_bid is not None:
        return Bid.objects.filter(auction=auction, amount=current_max_bid).first().bidder  # Get the object
    return None


def calc_currencies(eur):
    req = urllib.request.Request('http://data.fixer.io/api/latest?access_key=11eeeae1a79825147e43036f8e3be744&symbols=USD,GBP,CAD&format=1&base=EUR')
    response = urllib.request.urlopen(req).read()
    json_r = json.loads(response.decode('utf-8'))
    rates = json_r['rates']
    dic = dict()
    dic['USD'] = '$'+str(round(float(rates['USD']) * float(eur), 2))
    dic['GBP'] = '£'+str(round(float(rates['GBP']) * float(eur), 2))
    dic['CAD'] = 'CA$'+str(round(float(rates['CAD']) * float(eur), 2))
    return dic
