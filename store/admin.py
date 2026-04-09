from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'created_at')
    list_filter = ('created_at',)


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
