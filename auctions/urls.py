from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("category/<str:category>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("newListing", views.createListing, name="createListing"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("auctions/close/<str:listing_id>", views.closeAuction, name="closeAuction"),
    path("auctions/<str:id>", views.listing, name="listing"),
    path("auctions/update_watchlist/<str:action>/<str:listing_id>", views.updateWatchlist, name="addToWatchlist"),
    path("auctions/add_comment/<str:listing_id>", views.addListingComment, name="addComment")
]