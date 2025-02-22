import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from app_products.models import Product
from app_catalog.models import CatalogItem
from app_order.models import Order, OrderProduct
from app_auth.models import Profile

class OrderViewsTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CatalogItem.objects.create(
            title='CatalogItemExample'
        )
        cls.user_1 = User.objects.create_user(
            username='TestUser_1', password='12345',
            first_name='UserName', email='test@test.tst'
        )
        cls.user_2 = User.objects.create_user(
            username='TestUser_2', password='12345'
        )

        cls.profile = Profile.objects.create(
            user=cls.user_1,
            phone=333123,
            default_city='Default City',
            default_address='Default Address',
            default_delivery_type='Default delivery',
            default_payment_type='Default payment'
        )

        cls.order_1 = Order.objects.create(
            delivery_type='ordinary',
            payment_type='online',
            total_cost=100.00,
            status='Pending',
            city='New York',
            address='123 Test St',
            user=cls.user_1,
            delivery_name='John Doe',
            delivery_email='john.doe@example.com',
            delivery_phone=1234567890
        )

        cls.order_2 = Order.objects.create(
            delivery_type='ordinary',
            payment_type='online',
            total_cost=100.00,
            status='Pending',
            city='New York',
            address='123 Test St',
            user=cls.user_1,
            delivery_name='John Doe',
            delivery_email='john.doe@example.com',
            delivery_phone=1234567890
        )
        cls.order_3 = Order.objects.create(
            delivery_type='ordinary',
            payment_type='online',
            total_cost=100.00,
            status='Pending',
            city='New York',
            address='123 Test St',
            user=cls.user_2,
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
            order=cls.order_1,
            product=cls.product_1,
            count=1
        )
        cls.order_product_2 = OrderProduct.objects.create(
            order=cls.order_1,
            product=cls.product_2,
            count=2
        )
        cls.order_product_3 = OrderProduct.objects.create(
            order=cls.order_2,
            product=cls.product_1,
            count=3
        )
        cls.order_product_4 = OrderProduct.objects.create(
            order=cls.order_3,
            product=cls.product_1,
            count=3
        )
        cls.order_product_5 = OrderProduct.objects.create(
            order=cls.order_3,
            product=cls.product_2,
            count=3
        )

        test_data = [
            {
                "id": cls.product_1.id,
                "price": cls.product_1.price,
                "count": 2
            },
            {
                "id": cls.product_2.id,
                "price": cls.product_2.price,
                "count": 1
            }
        ]
        cls.test_data = json.dumps(test_data)

        cls.client = APIClient()


    def test_history_orders_for_unauthenticated(self):
        """Test get history of orders for unauthenticated"""
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_history_orders_for_authenticated(self):
        """Test get history of orders for authenticated first user & second user"""
        # For User 1 should be two orders
        self.client.login(username=self.user_1.username, password='12345')
        response = self.client.get('/api/orders')
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.client.logout()

        # For User 2 should be one order
        self.client.login(username=self.user_2.username, password='12345')
        response = self.client.get('/api/orders')
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)

        set_should_be = {
            'id', 'status', 'city', 'address', 'email',
            'phone', 'createdAt', 'fullName',
            'deliveryType', 'paymentType', 'totalCost',
            'products'
        }

        data = data[0]
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
        self.client.logout()

    def test_post_order_for_unauthenticated(self):
        """Test posting orders for unauthenticated"""

        response = self.client.post(
            '/api/orders', data=self.test_data, content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_creation_for_authenticated(self):
        """Test post order and get him from database and from GET url for authenticated"""

        self.client.login(username=self.user_1.username, password='12345')
        response = self.client.post(
            '/api/orders', data=self.test_data, content_type='application/json'
        )
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(data), {'orderId'})
        order_id = data['orderId']

        # Check from database
        created_order = Order.objects.get(pk=order_id)
        self.assertEqual(created_order.user, self.user_1)
        # be careful here, it is float numbers
        self.assertEqual(
            float(created_order.total_cost),
            self.product_1.price * 2 + self.product_2.price
        )
        self.assertEqual(created_order.delivery_name, self.profile.user.first_name)
        self.assertEqual(created_order.delivery_email, self.profile.user.email)
        self.assertEqual(created_order.delivery_phone, self.profile.phone)
        self.assertEqual(created_order.city, self.profile.default_city)
        self.assertEqual(created_order.address, self.profile.default_address)
        self.assertEqual(created_order.delivery_type, self.profile.default_delivery_type)
        self.assertEqual(created_order.payment_type, self.profile.default_payment_type)
        self.assertEqual(created_order.status, 'Products selected')

        product_from_order = created_order.order_product.first()
        self.assertEqual(product_from_order.product, self.product_1)
        self.assertEqual(product_from_order.count, 2)

        # Check from GET url
        response = self.client.get(f'/api/order/{order_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # be careful here, it is float numbers
        self.assertEqual(
            data['totalCost'],
            str(self.product_1.price * 2 + self.product_2.price)
        )
        self.assertEqual(data['fullName'], self.profile.user.first_name)
        self.assertEqual(data['email'], self.profile.user.email)
        self.assertEqual(data['phone'], self.profile.phone)
        self.assertEqual(data['city'], self.profile.default_city)
        self.assertEqual(data['address'], self.profile.default_address)
        self.assertEqual(data['deliveryType'], self.profile.default_delivery_type)
        self.assertEqual(data['paymentType'], self.profile.default_payment_type)
        self.assertEqual(data['status'], 'Products selected')
        self.assertIsInstance(data['createdAt'], str)
        self.assertIsInstance(data['products'], list)
        self.assertEqual(len(data['products']), 2)

        if data['products'][0]['title'] == 'Product for tests # 1':
            self.assertEqual(data['products'][0]['count'], 2)
            self.assertEqual(data['products'][1]['title'], 'Product for tests # 2')
            self.assertEqual(data['products'][1]['count'], 1)
        else:
            self.assertEqual(data['products'][0]['count'], 1)
            self.assertEqual(data['products'][1]['title'], 'Product for tests # 1')
            self.assertEqual(data['products'][1]['count'], 2)

        self.client.logout()

    def test_order_update_for_unauthenticated(self):
        """Test posting order for unauthenticated"""

        response = self.client.post(
            '/api/order/1',
            data='{"data": "data"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_update(self):
        """Test updating order"""
        self.client.login(username=self.user_1.username, password='12345')
        order_id = self.order_1.id
        data_for_update = {
            'deliveryType': 'Test update order',
            'paymentType': 'Test update order',
            'city': 'Test update order',
            'address': 'Test update order'
        }

        response = self.client.post(
            f'/api/order/{order_id}',
            data=json.dumps(data_for_update),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data, {'orderId': order_id})
        order = Order.objects.get(pk=order_id)

        self.assertEqual(order.delivery_type, 'Test update order')
        self.assertEqual(order.payment_type, 'Test update order')
        self.assertEqual(order.city, 'Test update order')
        self.assertEqual(order.address, 'Test update order')
        self.assertEqual(order.status, 'Waiting for payment')

        self.client.logout()

    def test_payment_for_unauthenticated(self):
        """Test posting payment for unauthenticated"""

        response = self.client.post(
            '/api/payment/1',
            data='{"data": "data"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_payments(self):
        """Test wrong payment url"""
        self.client.login(username=self.user_1.username, password='12345')

        order_id = self.order_1.id
        data_for_update_bad_1 = {
            "name":"Alex Fishman",
            "number":"123456789",
            "year":"24",
            "month":"12",
            "code":"123"
        }
        response = self.client.post(
            f'/api/payment/{order_id}',
            data=json.dumps(data_for_update_bad_1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'bed number')

        data_for_update_bad_2 = {
            "name": "Alex Fishman",
            "number": "1234567",
            "year": "24",
            "month": "12",
            "code": "123"
        }
        response = self.client.post(
            f'/api/payment/{order_id}',
            data=json.dumps(data_for_update_bad_2),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['message'], 'bed number')

        self.client.logout()

    def test_payment(self):
        """Test payment url"""
        self.client.login(username=self.user_1.username, password='12345')

        order_id = self.order_1.id

        data_for_update = {
            "name": "Alex Fishman",
            "number": "12345678",
            "year": "24",
            "month": "12",
            "code": "123"
        }
        response = self.client.post(
            f'/api/payment/{order_id}',
            data=json.dumps(data_for_update),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
