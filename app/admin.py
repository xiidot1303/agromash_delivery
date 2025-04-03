from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, CartItem, Store, StoreProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'bitrix_id', 'price', 'size', 'car_brand', 'type')
    search_fields = ('title', 'bitrix_id', 'car_brand')
    list_filter = ('type',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'status', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'customer_email')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('bot_user', 'created_at', 'updated_at')
    search_fields = ('bot_user__name', 'bot_user__phone')
    inlines = [CartItemInline]

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'bitrix_id', 'address')
    search_fields = ('title', 'bitrix_id', 'address')

@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ('store', 'product', 'quantity')
    search_fields = ('store__title', 'product__title')
    list_filter = ('store',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
