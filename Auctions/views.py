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
from django.contrib.auth.decorators import user_passes_test
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
                                         "The deadline has to be at least 72 hours in the future!")
                if min_price < 0:
                    messages.add_message(request, messages.ERROR,
                                         "The minimum price has to be at least 0!")
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
                auction = Auction(title=title, description=desc, min_price=min_price, deadline=deadline)
                auction.seller = request.user
                auction.save()
                to_email = [request.user.email]
                subject = "Auction " + title + " created!"
                message = "Your auction " + title + " has been successfully created on the YAAS Web Application!"
                send_email(subject, message, to_email)
    return redirect("index")


def send_email(subject, message, to_email):
    from_email = "YAASAuctionSite@noreply.com"
    with mail.get_connection() as connection:
        mail.EmailMessage(subject, message, from_email, to_email, connection=connection).send(fail_silently=False)


class AuctionView(View):
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            bid_form = MakeBidForm()
            bid_form.helper.form_action = reverse("auction_view", kwargs={'auction_id': auction_id})
            current_bid = get_max_bid(auction)
            return render(request, "auction.html", {'auction': auction, 'form': bid_form, "max_bid": current_bid})
        except Auction.DoesNotExist:
            messages.warning(request, "There is no auction with that id!")
            return redirect("index")

    def post(self, request, auction_id):
        bid_form = MakeBidForm(request.POST)
        auction = Auction.objects.get(id=auction_id)
        current_winner = get_current_winner(auction)
        curr_bid = get_max_bid(auction)
        #  Check if description changed?
        if auction.status == Auction.STATUS_ACTIVE:
            if auction.seller != request.user:
                if current_winner != request.user:
                    if bid_form.is_valid():
                        new_bid = bid_form.cleaned_data['bid']
                        if curr_bid is None:
                            cmp = auction.min_price
                        else:
                            cmp = curr_bid.amount
                        if ((new_bid > cmp) and curr_bid is not None) or ((new_bid >= cmp) and cmp == auction.min_price):
                            bid = Bid(bidder=request.user, auction=auction, amount=new_bid)
                            bid.save()
                            curr_bid = bid
                            bid_form = MakeBidForm()
                            bid_form.helper.form_action = reverse("auction_view", kwargs={'auction_id': auction_id})
                        else:
                            if cmp == auction.min_price:
                                messages.warning(request, "Your bid has to be greater than or equal to the minimum price!")
                            else:
                                messages.warning(request, "Your bid has to be greater than the currently winning bid!")
                else:
                    messages.warning(request, "You already have the highest bid!")
            else:
                messages.warning(request, "You cannot bid on your own auctions!")
        else:
            messages.warning(request, "This auction is no longer active!")

        return render(request, "auction.html", {'auction': auction, 'form': bid_form, "max_bid": curr_bid})


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
                    messages.warning(request, "You cannot edit this auction because it is no longer active!")
            else:
                messages.warning(request, "You are not allowed to edit this auction!")
        except Auction.DoesNotExist:
            messages.warning(request, "There is no auction with that id!")
        return redirect("index")

    def post(self, request, auction_id):
        auction = Auction.objects.get(id=auction_id)
        if auction is not None:
            if auction.status == Auction.STATUS_ACTIVE:
                auction.description = request.POST['description']
                auction.save()
                return redirect("auction_view", auction_id=auction_id)
            else:
                messages.warning(request, "This auction is no longer active!")
        else:
            messages.warning(request, "There is no auction with that id!")
        return redirect("index")


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class BanAuction(View):
    def get(self, request, auction_id):
        print("Hej")

    def post(self,request, auction_id):
        pass


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
