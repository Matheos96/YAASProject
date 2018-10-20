from rest_framework import serializers
from Auctions.models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    winning_bid = serializers.SlugRelatedField(many=False, read_only=True, slug_field='amount', allow_null=True)
    seller = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username', allow_null=False)

    class Meta:
        model = Auction
        fields = ('id', 'url', 'title', 'description', 'deadline', 'min_price', 'winning_bid', 'seller')

