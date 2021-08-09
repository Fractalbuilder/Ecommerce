from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=34)
    category = models.CharField(max_length=20)
    price = models.IntegerField()
    img_url = models.CharField(max_length=300, blank=True, default='')
    description = models.CharField(max_length=55)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    state = models.CharField(max_length=6, default='open')

class Bid(models.Model):
    listing = models.OneToOneField(AuctionListing, on_delete=models.CASCADE, related_name="bid_listing")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_amount = models.IntegerField()

class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comment_listing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    comment = models.CharField(max_length=150)

class Watchlist(models.Model):
    class Meta: # Composite pk
        unique_together = (('watcher', 'listing'),)

    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="listing")