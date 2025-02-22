from django.db import models
from django.contrib.auth.models import User

from app_products.models import Product


class BasketItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='basket')
    count = models.PositiveIntegerField(verbose_name='Count')
