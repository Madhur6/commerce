from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing/", views.new_listing, name="new_listing"),
    path("go_to_listing/<int:id>", views.go_to_listing, name="go_to_listing"),
    path("add_watchlist/<int:id>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:id>", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("go_to_category/", views.go_to_category, name="go_to_category"),
    path("comments/<int:id>", views.comments, name="comments"),
    path("bids/<int:id>", views.bids, name="bids"),
    path("close_the_listing/<int:id>", views.close_the_listing, name="close_the_listing")
]
