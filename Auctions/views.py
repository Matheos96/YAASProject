from django.shortcuts import render
from .forms import *

# Create your views here.


def new_auction(request):
    if request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            form.save()
            #return redirect("index")

    else:
        form = AuctionForm()

    context = {"form": form}
    return render(request, "new_auction.html", context)