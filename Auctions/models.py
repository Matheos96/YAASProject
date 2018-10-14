from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    min_price = models.DecimalField(max_digits=9,decimal_places=2)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False)
    seller = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

