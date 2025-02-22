from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from app_products.models import Product
from app_catalog.models import CatalogItem
from app_order.models import Order, OrderProduct
from app_order.serializers import OrderSerializer, ProductSerializerForOrders

class OrderSerializersTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CatalogItem.objects.create(
            title='CatalogItemExample'
        )
        cls.user = User.objects.create_user(
            username='TestUser', password='12345'
        )

        cls.order = Order.objects.create(
            delivery_type='ordinary',
            payment_type='online',
            total_cost=100.00,
            status='Pending',
            city='New York',
            address='123 Test St',
            user=cls.user,
            delivery_name='John Doe',
            delivery_email='john.doe@example.com',
            delivery_phone=1234567890
        )

        cls.product_1 = Product.objects.create(
            title='Product for tests # 1',
            description='Description of product # 1 for test',
            price=1.99,
            count=2,
            rating=5,
            category=cls.category
        )
        cls.product_2 = Product.objects.create(
            title='Product for tests # 2',
            description='Description of product # 2 for test',
            price=15.99,
            count=3,
            rating=5,
            category=cls.category
        )
        cls.order_product_1 = OrderProduct.objects.create(
            order=cls.order,
            product=cls.product_1,
            count=1
        )
        cls.order_product_2 = OrderProduct.objects.create(
            order=cls.order,
            product=cls.product_2,
            count=2
        )


    def test_product_for_catalog_serializer(self):
        """Test OrderSerializer"""

        serializer = OrderSerializer(Order.objects.all(), many=True)
        data = serializer.data[0]
        set_should_be = {
            'id', 'status', 'city', 'address', 'email',
            'phone', 'createdAt', 'fullName',
            'deliveryType', 'paymentType', 'totalCost',
            'products'
        }

        self.assertEqual(set(data), set_should_be)

        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['status'], str)
        self.assertIsInstance(data['city'], str)
        self.assertIsInstance(data['address'], str)
        self.assertIsInstance(data['email'], str)
        self.assertIsInstance(data['phone'], int)
        self.assertIsInstance(data['createdAt'], str)
        self.assertIsInstance(data['fullName'], str)
        self.assertIsInstance(data['deliveryType'], str)
        self.assertIsInstance(data['paymentType'], str)
        self.assertIsInstance(data['totalCost'], str)
        self.assertIsInstance(data['products'], list)

        self.assertEqual(len(data['products']), 2)

    def test_product_for_order_serializer(self):
        """Test ProductSerializerForOrders"""
        qs = Product.objects.all()

        serializer = ProductSerializerForOrders(qs.get(title='Product for tests # 1'))
        data = serializer.data
        set_should_be = {
            'id', 'price', 'count', 'date', 'title',
            'description', 'freeDelivery', 'rating',
            'tags', 'images', 'reviews', 'category',
            'fullDescription'
        }

        self.assertEqual(set(data), set_should_be)
        self.assertEqual(data['title'], 'Product for tests # 1')

        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['images'], list)
        self.assertEqual(data['reviews'], 0)
        self.assertEqual(data['category'], self.product_1.category.id)
        self.assertEqual(data['price'], self.product_1.price)
        self.assertEqual(data['fullDescription'], self.product_1.description)
        self.assertEqual(data['description'], self.product_1.description[:20] + '...')
        self.assertEqual(data['freeDelivery'], False) #default value
        self.assertEqual(data['rating'], self.product_1.rating)
