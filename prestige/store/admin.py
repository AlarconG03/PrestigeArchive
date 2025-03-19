from django.contrib import admin
from .models import Product, Order, OrderItem, User, Newsletter, Favorite, Address
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Favorite)
admin.site.register(Address)
admin.site.register(Newsletter)
admin.site.register(User, UserAdmin)