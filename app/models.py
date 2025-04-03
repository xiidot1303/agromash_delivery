from django.db import models
from bot.models import Bot_user
from asgiref.sync import sync_to_async


class Product(models.Model):
    title = models.CharField(max_length=255)
    size = models.CharField(max_length=16)
    car_brand = models.CharField(max_length=255)
    TYPE_CHOICES = [
        (97, "Аккумулятор"),
        (99, "Балон"),
        (101, "Диска"),
        (103, "Масло"),
    ]
    type = models.IntegerField(choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    photo = models.FileField(upload_to="product/photo/", null=True, blank=True)
    remaining = models.IntegerField()

    def __str__(self):
        return self.title

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ])
    bot_user = models.ForeignKey(Bot_user, on_delete=models.CASCADE, related_name='orders')
    delivery_time = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    payment_type = models.CharField(max_length=50, null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_user = models.ForeignKey(Bot_user, on_delete=models.CASCADE, related_name='carts')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    @sync_to_async
    def get_product(self):
        return self.product