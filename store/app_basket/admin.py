from django.contrib import admin

from .models import BasketItem


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'product', 'count'
