from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect

from django import forms
from .models import User, AuctionListing, Watchlist, Bid, Comment

categoryList = [
    ('cars', 'Cars'),
    ('cleaning', 'Cleaning'),
    ('toys', 'Toys'),
    ]

def ValidateAlphanumeric(value):
    if not value.isalnum():
        raise forms.ValidationError("Only alpha-numeric characters are allowed")

class CommentForm(forms.Form):
    comment = forms.CharField(label="Comment", widget=forms.TextInput(attrs={'class': 'form-control col-md-10 col-lg-10 formItem', 'placeholder': 'Comment'}))

class BidForm(forms.Form):
    bid_amount = forms.IntegerField(label="New bid", widget=forms.TextInput(attrs={'class': 'form-control col-md-3 col-lg-3 formItem', 'placeholder': 'Bid'}))

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control col-md-3 col-lg-3', 'placeholder': 'Title'}), validators=[ValidateAlphanumeric])
    category = forms.CharField(label='Category', widget=forms.Select(choices=categoryList, attrs={'class': 'form-control col-md-2 col-lg-2'}), required=False)
    price = forms.IntegerField(label="Price", error_messages={'invalid': 'Only integers are allowed'}, widget=forms.TextInput(attrs={'class': 'form-control col-md-1 col-lg-1', 'placeholder': 'Price'}))
    img_url = forms.CharField(label="Img url", widget=forms.TextInput(attrs={'class': 'form-control col-md-5 col-lg-5', 'placeholder': 'Image URL (Optional)'}), required=False)
    description = forms.CharField(label="Description", widget=forms.TextInput(attrs={'class': 'form-control col-md-4 col-lg-4', 'placeholder': 'Description'}))

def addListingComment(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)

    commentForm = CommentForm(request.POST)
    comment = commentForm['comment'].value()
    Comment(listing=listing, user=request.user, comment=comment).save()
    
    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing_id}))

def applyBid(newAmount, listing, user):
    existingBid = Bid.objects.all().filter(listing=listing).first()
    
    if(existingBid is None):
        if(newAmount > listing.price):
            Bid(listing=listing, bidder=user, bid_amount=newAmount).save()
            listing.price = newAmount
            listing.save()

            return True
        else:
            return False
    else:
        if(newAmount > existingBid.bid_amount):
            existingBid.bid_amount = newAmount
            existingBid.save()
            
            listing.price = newAmount
            listing.save()

            return True
        else:
            return False

def bid(request, listing):
    Bid = BidForm(request.POST)

    if form.is_valid():
        return HttpResponseRedirect(reverse("listing", kwargs={'id': listing_id}))
    else:
        return HttpResponseRedirect(reverse("listing", kwargs={'id': listing_id}))

def categories(request):
    reducedCategoryList = []

    for i in categoryList:
        reducedCategoryList.append(list(i)[1])

    return render(request, "auctions/categories.html", {"categories": reducedCategoryList})

def category(request, category):
    listings = AuctionListing.objects.all().filter(category=category).values()
    return render(request, "auctions/index.html", {"listings": listings})

def closeAuction(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    listing.state = "closed"
    listing.save()

    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing_id}))

def createListing(request):
    if request.method != "POST":
        return render(request,"auctions/new_listing.html", {"form": NewListingForm()})
    else:
        form = NewListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            category = form.cleaned_data["category"]
            price = form.cleaned_data["price"]
            img_url = form.cleaned_data["img_url"]
            description = form.cleaned_data["description"]

            existingListing = AuctionListing.objects.all().filter(title=title).first()

            if(existingListing is None):
                listing = AuctionListing(title=title, category=category, price=price, img_url=img_url, description=description, owner=request.user).save()
                #Bid(listing=listing, bidder=category, bid_amount=price).save()
                
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "auctions/new_listing.html", {
                    "form": form,
                    "existing": True
                })
        else:
            return render(request, "auctions/new_listing.html", {"form": form})

def index(request):
    listings = AuctionListing.objects.all().values()
    return render(request, "auctions/index.html", {"listings": listings})

def listing(request, id):
    listing = AuctionListing.objects.get(id=id)
    isWatched = Watchlist.objects.all().filter(watcher=request.user.id, listing=id).first()

    if isWatched is None:
        isWatched = False
    else:
        isWatched = True

    comments = Comment.objects.all().filter(listing=listing)
    
    if listing.state == "open":
        if request.method != "POST":
            return render(request, "auctions/listing.html", {"listing": listing, "commentForm": CommentForm(), "comments": comments, 'bidForm': BidForm(), "isBidValid": None, "isWatched": isWatched})
        else:
            bidForm = BidForm(request.POST)
            
            if bidForm.is_valid():
                bid_amount = bidForm.cleaned_data["bid_amount"]

                if applyBid(bid_amount, listing, request.user):
                    updatedListing = AuctionListing.objects.get(id=id)
                    bidForm = BidForm()

                    return render(request, "auctions/listing.html", {"listing": updatedListing, "commentForm": CommentForm(), "comments": comments, 'bidForm': BidForm(), "isBidValid": True, "isWatched": isWatched})
                else:
                    return render(request, "auctions/listing.html", {"listing": listing, "commentForm": CommentForm(), "comments": comments, 'bidForm': bidForm, "isBidValid": False, "isWatched": isWatched})
            else:
                return render(request, "auctions/listing.html", {"listing": listing, "commentForm": CommentForm(), "comments": comments, 'bidForm': bidForm, "isWatched": isWatched})
    else:
        existingBid = Bid.objects.all().filter(listing_id=listing).first()

        if existingBid is None:
            auctionWinner = False
        else:
            if existingBid.bidder == request.user:
                auctionWinner = True
            else:
                auctionWinner = False

        return render(request, "auctions/listing.html", {"listing": listing, "isWatched": isWatched, "auctionClosed": True, "auctionWinner": auctionWinner})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def updateWatchlist(request, action, listing_id):
    if action == "Delete":
        Watchlist.objects.all().filter(listing=listing_id).delete()
    else:
        user = User.objects.get(id=request.user.id)
        listing = AuctionListing.objects.get(id=listing_id)
        Watchlist(watcher=user, listing=listing).save()

    return HttpResponseRedirect(reverse("listing", kwargs={'id': listing_id}))

def watchlist(request):
    watchlist = Watchlist.objects.all().filter(watcher=request.user)
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist})