from django.db import models
from django.contrib.auth.models import User
from concurrency.fields import ConditionalVersionField
# Create your models here.


class Auction(models.Model):
    STATUS_BANNED = 1
    STATUS_ACTIVE = 2
    STATUS_DUE = 3
    STATUS_CHOICES = ((STATUS_BANNED, 'Banned'),
                      (STATUS_ACTIVE, 'Active'),
                      (STATUS_DUE, 'Due'))

    title = models.CharField(max_length=150, blank=False)
    description = models.TextField(blank=False)
    min_price = models.DecimalField(max_digits=9, decimal_places=2, blank=False)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False)
    seller = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='created_by')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    winning_bid = models.ForeignKey('Bid', null=True, blank=True, on_delete=models.CASCADE, related_name='winning_bid')
    version = ConditionalVersionField('winning_bid')  # Handle concurrency

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['deadline']


class Bid(models.Model):
    auction = models.ForeignKey(Auction, null=False, on_delete=models.CASCADE, related_name='made_on')
    bidder = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='bid_created_by')
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return self.auction.title + ", " + self.bidder.username
