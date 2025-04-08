from django.db import models
from bot.models import Bot_user
from asgiref.sync import sync_to_async


class Product(models.Model):
    bitrix_id = models.IntegerField(unique=True, null=True)
    title = models.CharField(max_length=255)
    size = models.CharField(max_length=16, null=True)
    car_brand = models.CharField(max_length=255, null=True)
    TYPE_CHOICES = [
        (97, "Аккумулятор"),
        (99, "Балон"),
        (101, "Диска"),
        (103, "Масло"),
    ]
    type = models.IntegerField(choices=TYPE_CHOICES, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True)
    photo = models.FileField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.title


class Store(models.Model):
    bitrix_id = models.IntegerField(unique=True, null=True)
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.store.title} - {self.product.title}"

    @property
    @sync_to_async
    def get_product(self):
        return self.product

    @property
    @sync_to_async
    def get_store(self):
        return self.store


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
    bot_user = models.ForeignKey(
        Bot_user, on_delete=models.CASCADE, related_name='orders')
    delivery_time = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    payment_type = models.CharField(max_length=50, null=True, blank=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot_user = models.ForeignKey(
        Bot_user, on_delete=models.CASCADE, related_name='carts')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    @sync_to_async
    def get_product(self):
        return self.product
