from django.contrib import admin
from .models import *

admin.site.register((
    Maincategory,
    Subcategory,
    Brand,
    Product,
    Seller,
    Buyer,
    Wishlist,
    Checkout,
    CheckoutProducts,
    Newsletter,
    Contact
))

# Register your models here.
