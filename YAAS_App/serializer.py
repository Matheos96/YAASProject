from rest_framework import serializers
from Auctions.models import Auction


class AuctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auction
        fields = ('id', 'url', 'title', 'description', 'deadline', 'min_price', 'winning_bid')

