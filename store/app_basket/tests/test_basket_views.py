import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from app_basket.models import BasketItem
from app_products.models import Product
from app_catalog.models import CatalogItem


class BasketViewsTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='TestUser', password='12345'
        )
        cls.category = CatalogItem.objects.create(
            title='CatalogItemExample'
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
            price=5.99,
            count=3,
            rating=2,
            category=cls.category
        )
        cls.basket_item = BasketItem.objects.create(
            user=cls.user,
            product=cls.product_1,
            count=1
        )


    def test_get_basket_view(self):
        """Test Get Basket"""
        self.client.login(username=self.user.username, password='12345')
        response = self.client.get('/api/basket')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        set_should_be = {
            'id', 'category', 'fullDescription', 'freeDelivery',
            'reviews', 'price', 'tags', 'images', 'rating', 'title',
            'count', 'date', 'description'
        }

        self.assertEqual(set(data), set_should_be)

        self.assertEqual(data['id'], self.basket_item.id)
        self.assertEqual(data['category'], self.category.id)
        self.assertEqual(data['fullDescription'], self.product_1.description)
        self.assertEqual(data['freeDelivery'], self.product_1.free_delivery)
        self.assertIsInstance(data['reviews'], int)
        self.assertEqual(data['price'], self.product_1.price)
        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['images'], list)
        self.assertEqual(data['rating'], self.product_1.rating)
        self.assertEqual(data['title'], self.product_1.title)
        self.assertEqual(data['count'], self.basket_item.count)
        self.assertIsInstance(data['date'], str)
        self.assertIsInstance(data['description'], str)



    def test_basket_view_normal_post_delete(self):
        """Test Post/Delete Basket"""
        self.client.login(username=self.user.username, password='12345')
        one_prod_1 = {
                'id': str(self.product_1.id),
                'count': 1
            }

        response = self.client.post(
            '/api/basket',
            data=json.dumps(one_prod_1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data[0]
        set_should_be = {
            'id', 'category', 'fullDescription', 'freeDelivery',
            'reviews', 'price', 'tags', 'images', 'rating', 'title',
            'count', 'date', 'description'
        }

        self.assertEqual(set(data), set_should_be)

        self.assertEqual(data['id'], self.basket_item.id)
        self.assertEqual(data['category'], self.category.id)
        self.assertEqual(data['fullDescription'], self.product_1.description)
        self.assertEqual(data['freeDelivery'], self.product_1.free_delivery)
        self.assertIsInstance(data['reviews'], int)
        self.assertEqual(data['price'], self.product_1.price)
        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['images'], list)
        self.assertEqual(data['rating'], self.product_1.rating)
        self.assertEqual(data['title'], self.product_1.title)
        self.assertEqual(data['count'], self.basket_item.count + 1)
        self.assertIsInstance(data['date'], str)
        self.assertIsInstance(data['description'], str)

        basket_item = BasketItem.objects.get(pk=self.basket_item.id)
        self.assertEqual(basket_item.count, self.basket_item.count + 1)

        response = self.client.delete(
            '/api/basket',
            data=json.dumps(one_prod_1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basket_item = BasketItem.objects.get(pk=self.basket_item.id)
        self.assertEqual(basket_item.count, self.basket_item.count)


    def test_basket_view_wrong_post(self):
        """Test trying to add too many goods to the basket"""
        self.client.login(username=self.user.username, password='12345')
        two_prod_1 = {
                'id': str(self.product_1.id),
                'count': 2
            }

        response = self.client.post(
            '/api/basket',
            data=json.dumps(two_prod_1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, 'too many goods')


    def test_basket_saved_after_login(self):
        """Test for saving of basket from cookies to database"""

        one_prod_1 = {
            'id': str(self.product_1.id),
            'count': 1
        }

        response = self.client.post(
            '/api/basket',
            data=json.dumps(one_prod_1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        basket_from_database = BasketItem.objects.get(user=self.user)
        self.assertEqual(basket_from_database.count, 1)

        # after logining
        data_in = {
            'username': self.user.username,
            'password': '12345'
        }
        response = self.client.post(
            '/api/sign-in',
            data=json.dumps(data_in),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basket_from_database = BasketItem.objects.get(user=self.user)
        self.assertEqual(basket_from_database.count, 2)
