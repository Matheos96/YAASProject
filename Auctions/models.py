from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=9,decimal_places=2)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False)
    seller = models.OneToOneField(User, blank=False, null=False, on_delete=models.CASCADE)
