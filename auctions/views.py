from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listings, Comments, Bids


from django.utils.datastructures import MultiValueDictKeyError



from django.contrib.auth.decorators import login_required


from django.db.models import Max




def index(request):
    available = Listings.objects.filter(available=True).order_by("-created_at")

    if request.user.is_authenticated:
        user = request.user
        watchlist_count = Listings.objects.filter(watchlist__in=[user]).count()
    else:
        watchlist_count = 0
    
    categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": available,
        "categories": categories,
        "watchlist_count": watchlist_count
    })


def new_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]

        image_url = request.POST["image_url"]
        try:
            category = request.POST["category"]
            if not category:
                raise MultiValueDictKeyError
        except MultiValueDictKeyError:
            categories = Category.objects.all()
            return render(request, "auctions/new_listing.html", {
                "message": "category field required!!",
                "categories": categories
            })

        if not (title and description and price):
            return render(request, "auctions/new_listing.html", {
                "message": "fields required!!"
            })
        
        try:
            categoryData = Category.objects.get(categoryData=category)
        except Category.DoesNotExist:
            return render(request, "auctions/new_listing.html", {
                "message": "choose valid category!"
            })

        owner = request.user

        listing = Listings.objects.create(owner=owner, title=title, description=description, price=price, category=categoryData, image_url=image_url)
        listing.save()

        return HttpResponseRedirect(reverse("index"))
    
    else:
        categories = Category.objects.all()
        return render(request, "auctions/new_listing.html", {
            "categories": categories
        })

    

def find_winner(listing):
    highest_bid = listing.bids.aggregate(Max("bid_amount"))["bid_amount__max"]

    if highest_bid is not None and not listing.available:
        obj = listing.bids.get(bid_amount=highest_bid)
        winner = obj.user
    else:
        winner = None

    return winner, highest_bid

def go_to_listing(request, id):
    try:
        listing = Listings.objects.get(pk=id)
    except:
        return render(request, "auctions/error.html",{
            "message": "page does not exists!"
        })
    watchlisted = request.user in listing.watchlist.all()
    comments = Comments.objects.filter(listing=listing).order_by("-comment_time")

    bids = Bids.objects.filter(listing=listing).count()

    owner = listing.owner

    winner, highest_bid = find_winner(listing)

    return render(request, "auctions/go_to_listing.html", {
        "bid_message": f"{bids} bid(s) so far. Your bid is current bid!",
        "listing": listing,
        "comments": comments,
        "watchlist": watchlisted,
        "owner": owner,
        "winner": winner,
        "highest_bid": highest_bid
    })



def comments(request, id):
    if request.method == "POST": 
        try:
            listing = Listings.objects.get(pk=id)
        except:
            return render(request, "auctions/error.html",{
                "message": "page does not exists!"
            })
        user = request.user

        if not user.is_authenticated:
            return render(request, "auctions/login.html", {
                "message": "please login first!"
            })

        comment_text = request.POST["comment"]

        if comment_text:
            #create a new comment instance and set it's attributes
            comment = Comments.objects.create(listing=listing, user=user, comment_text=comment_text)
            comment.save()

        return HttpResponseRedirect(reverse("go_to_listing", args=(id,)))
    return HttpResponseRedirect(reverse("go_to_listing", args=(id,)))




def add_watchlist(request, id):
    listing = Listings.objects.get(pk=id)

    user = request.user

    listing.watchlist.add(user)

    return HttpResponseRedirect(reverse("go_to_listing", args=(id,)))


def remove_watchlist(request, id):
    listing = Listings.objects.get(pk=id)

    owner = request.user

    listing.watchlist.remove(owner)

    return HttpResponseRedirect(reverse("go_to_listing", args=(id,)))


def watchlist(request):
    user = request.user

    watchlist = user.watchlist.all()

    watchlist_count = Listings.objects.filter(watchlist__in=[user]).count()

    return render(request, "auctions/watchlist.html", {
        "listings": watchlist,
        "watchlist_count": watchlist_count
    })


def go_to_category(request):
    if request.method == "POST":
        categories = Category.objects.all()

        category = request.POST["category"]
        categoryData = Category.objects.get(categoryData=category)

        listing = Listings.objects.filter(available=True, category=categoryData)

        return render(request, "auctions/index.html", {
            "listings": listing,
            "categories": categories
        })



def bids(request, id):
    try:
        listing = Listings.objects.get(pk=id)
    except:
        return render(request, "auctions/error.html", {
            "message": "page does not exists!"
        })

    user = request.user

    if not user.is_authenticated:
        return render(request, "auctions/login.html", {
            "message": "please login first!"
        })

    try:
        bid_amount = float(request.POST["bids"])
    except ValueError:
        redirect_url = request.META.get("HTTP_REFERER")
        return render(request, "auctions/error.html", {
            "message": "Invalid bid amount! Choose a valid amount.",
            "redirect_url": redirect_url
        })

    try:
        starting_price = float(listing.price)
    except Listings.DoesNotExist:
        return render(request, "auctions/error.html", {
            "message": "listing does not exists!"
        })

    current_highest_bid = Bids.objects.filter(listing=listing).aggregate(Max("bid_amount"))["bid_amount__max"] or 0.0
    # if current_highest_bid is None:
    #     current_highest_bid = starting_price

    if (bid_amount > float(current_highest_bid) and bid_amount >= starting_price):
        #create a new instance and store the bid's data in it
        bid = Bids.objects.create(listing=listing, user=user, bid_amount=bid_amount)
        bid.save()
    else:

        go_to_listing = reverse('go_to_listing', args=(id,))

        message = "Your bid does not match the current highest bid on the listing, Try higher amount!"

        redirect_url = reverse('go_to_listing', args=(id,))

        return render(request, "auctions/error.html", {
            "message": message,
            "redirect_url": redirect_url,
        })
        

    return HttpResponseRedirect(reverse("go_to_listing", args=(id,)))



def close_the_listing(request, id):
    
    try:
        listing = Listings.objects.get(pk=id)
    except Listings.DoesNotExist:
        return render(request, "auctions/error.html", {
            "message": "page does not exists!"
        })
    
    highest_bid = listing.bids.aggregate(Max("bid_amount"))["bid_amount__max"]

    if highest_bid is not None:
        obj = listing.bids.get(bid_amount=highest_bid)
        winner = obj.user
    else:
        winner = None

    # winner, highest_bid = find_winner(listing)

    listing.available = False
    listing.save()

    redirect_url = reverse("index")

    return render(request, "auctions/winner.html", {
        "highest_bid": highest_bid,
        "winner": winner,
        "listing": listing,
        "redirect_url": redirect_url,
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if not(username and password):
            return render(request, "auctions/login.html", {
                "message": "both fields are required!!"
            })

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

        if not (username and email and password and confirmation):
            return render(request, "auctions/register.html", {
                "message": "All fields are required!!"
            })
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match!"
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        except ValueError:
            return render(request, "auctions/register.html", {
                "message": "username required!"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
