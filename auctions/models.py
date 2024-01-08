from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryData = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.categoryData}"


class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=300)
    available = models.BooleanField(default=True)
    price = models.FloatField(validators=[MinValueValidator(0)], default=0.0)
    image_url = models.URLField(blank=True, null=True)

    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listing")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")


    def __str__(self):
        return f"listing {self.id}: {self.title}"
    


class Comments(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, blank=True, null=True, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="comment_made")

    comment_text = models.TextField(max_length=1000)
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"comment {self.id} on {self.listing.title} by {self.user.username}"
    

class Bids(models.Model):
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_placed")

    bid_amount = models.FloatField(validators=[MinValueValidator(0)], default=0.0)
    bid_time = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Bid {self.id} on {self.listing.title} by {self.user.username}"
