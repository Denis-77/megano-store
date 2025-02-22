from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from app_products.models import Product
from app_catalog.models import CatalogItem
from app_order.models import Order, OrderProduct

class OrderTestCase(APITestCase):

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

        cls.product = Product.objects.create(
            title='Product for tests # 1',
            description='Description of product # 1 for test',
            price=1.99,
            count=3,
            rating=5,
            category=cls.category
        )
        cls.order_product = OrderProduct.objects.create(
            order=cls.order,
            product=cls.product,
            count=2
        )


    def test_order_creation(self):
        """Test creation order"""
        self.assertEqual(self.order.delivery_type, 'ordinary')
        self.assertEqual(self.order.payment_type, 'online')
        self.assertEqual(self.order.total_cost, 100.00)
        self.assertEqual(self.order.status, 'Pending')
        self.assertEqual(self.order.city, 'New York')
        self.assertEqual(self.order.address, '123 Test St')
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.delivery_name, 'John Doe')
        self.assertEqual(self.order.delivery_email, 'john.doe@example.com')
        self.assertEqual(self.order.delivery_phone, 1234567890)


    def test_create_order_product(self):
        """Test creation order-product"""
        self.assertEqual(self.order_product.order, self.order)
        self.assertEqual(self.order_product.product, self.product)
        self.assertEqual(self.order_product.count, 2)
