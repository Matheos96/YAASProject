from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View

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
                subject = "Auction " + title + " created!"
                to_email = [request.user.email]
                message = "Your auction " + title + " has been successfully created on the YAAS Web Application!"
                from_email = "YAASAuctionSite@noreply.com"
                send_mail(subject=subject, message=message, recipient_list=to_email, from_email=from_email, fail_silently=False)

    return redirect("index")


class AuctionView(View):
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            context = {"auction_title": auction.title, "auction_description": auction.description,
                       "auction_min_price": auction.min_price, "auction_deadline": auction.deadline,
                       "auction_seller": auction.seller, "auction_id": auction_id}
            return render(request, "auction.html", context)
        except Auction.DoesNotExist:
            messages.warning(request, "There is no auction with that id!")
            return redirect("index")


@method_decorator(login_required, name='dispatch')
class EditAuction(View):
    def get(self, request, auction_id):
        try:
            auction = Auction.objects.get(id=auction_id)
            if request.user == auction.seller:
                form = EditAuctionForm(instance=auction)
                return render(request, "edit_auction.html", {"form": form})
            else:
                messages.warning(request, "You are not allowed to edit this auction!")
        except Auction.DoesNotExist:
            messages.warning(request, "There is no auction with that id!")
        return redirect("index")

    def post(self, request, auction_id):
        auction = Auction.objects.get(id=auction_id)
        if auction is not None:
            auction.description = request.POST['description']
            auction.save()
            return redirect("auction_view", auction_id=auction_id)
        return redirect("index")


