from django.contrib import admin

from app_order.models import Order, OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date_created', 'delivery_type', 'payment_type', 'total_cost',
        'status', 'city', 'address', 'user', 'delivery_name', 'delivery_email',
        'delivery_phone'
    )


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'order', 'count'
    )
