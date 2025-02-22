from rest_framework import serializers
from django.contrib.auth.models import User

from app_order.models import Order
from app_catalog.serializers import ProductSerializerForCatalog


class ProfileForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'email', 'phone'
        ]


class ProductSerializerForOrders(ProductSerializerForCatalog):
    def get_reviews(self, instance):
        return len(instance.review_set.all())


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    email = serializers.EmailField(source='delivery_email')
    phone = serializers.IntegerField(max_value=9223372036854775807, source='delivery_phone')

    def get_products(self, obj):
        products = []
        for order_product in obj.order_product.all():
            order_product.product.count = order_product.count
            products.append(order_product.product)
        return ProductSerializerForOrders(products, many=True).data

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['createdAt'] = result.pop('date_created')
        result['fullName'] = result.pop('delivery_name')
        result['deliveryType'] = result.pop('delivery_type')
        result['paymentType'] = result.pop('payment_type')
        result['totalCost'] = result.pop('total_cost')
        return result

    class Meta:
        model = Order
        fields = [
            'id', 'date_created', 'delivery_type', 'payment_type',
            'total_cost', 'status', 'city', 'address', 'delivery_name',
            'email', 'phone', 'products',
        ]
