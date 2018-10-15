from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Auction(models.Model):
    STATUS_BANNED = 1
    STATUS_ACTIVE = 2
    STATUS_DUE = 3
    STATUS_CHOICES = ((STATUS_BANNED, 'Banned'),
                      (STATUS_ACTIVE, 'Active'),
                      (STATUS_DUE, 'Due'))

    title = models.CharField(max_length=150)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=9, decimal_places=2)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False)
    seller = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='created_by')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    def __str__(self):
        return self.title


class Bid(models.Model):
    auction = models.ForeignKey(Auction, null=False, on_delete=models.CASCADE, related_name='made_on')
    bidder = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='bid_created_by')
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=False)

    def __str__(self):
        return self.auction.title + ", " + self.bidder.username
