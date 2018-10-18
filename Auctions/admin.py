from django.contrib import admin
from .models import *
# Register your models here.


class AuctionAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'min_price', 'deadline', 'seller', 'status']


class BidAdmin(admin.ModelAdmin):
    list_display = ['auction', 'bidder', 'amount']


admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
