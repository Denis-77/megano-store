from django.db import models
from django.contrib.auth.models import User

from app_products.models import Product


class Order(models.Model):
    date_created = models.DateTimeField('Order created time', auto_now_add=True)
    delivery_type = models.CharField(verbose_name='Type of delivery', max_length=255)
    payment_type = models.CharField(verbose_name='Type of payment', max_length=255)
    total_cost = models.DecimalField(verbose_name='Total cost', max_digits=10, decimal_places=2)
    status = models.CharField(verbose_name='Status', max_length=50)
    city = models.CharField(verbose_name='Delivery city', max_length=50)
    address = models.CharField(verbose_name='Delivery address', max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_name = models.CharField(verbose_name='Full name for delivery', max_length=149)
    delivery_email = models.EmailField(verbose_name='Email for delivery')
    delivery_phone = models.PositiveBigIntegerField(
        verbose_name='Phone number for delivery', null=True, blank=True, default=0
    )


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_product')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(verbose_name='Count')

