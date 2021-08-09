from django.contrib import admin
from .models import AuctionListing, Watchlist, Bid, Comment

# Register your models here.
admin.site.register(AuctionListing)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)