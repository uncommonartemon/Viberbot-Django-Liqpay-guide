from django.contrib import admin
from .models import Product, Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'seller', 'weight', 'image')