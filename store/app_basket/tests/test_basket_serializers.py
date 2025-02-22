from django.db.models import Count
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from app_basket.models import BasketItem
from app_products.models import Product
from app_catalog.models import CatalogItem
from app_basket.serializers import BasketSerializer, AnonymBasket


class BasketSerializersTestCase(APITestCase):

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
            count=3,
            rating=5,
            category=cls.category
        )
        cls.product_2 = Product.objects.create(
            title='Product for tests # 2',
            description='Description of product # 2 for test',
            price=5.99,
            count=6,
            rating=2,
            category=cls.category
        )
        cls.basket_item_1 = BasketItem.objects.create(
            user=cls.user,
            product=cls.product_1,
            count=2
        )
        cls.basket_item_2 = BasketItem.objects.create(
            user=cls.user,
            product=cls.product_2,
            count=3
        )


    def test_basket_serializer(self):
        """Test BasketSerializer"""
        qs = Product.objects.annotate(Count('review'))
        serializer = BasketSerializer(qs, many=True)
        self.assertEqual(len(qs), 2)
        data = serializer.data[0]
        set_should_be = {
            'id', 'category', 'fullDescription', 'freeDelivery',
            'reviews', 'price', 'tags', 'images', 'rating', 'title',
            'count', 'date', 'description'
        }

        self.assertEqual(set(data), set_should_be)

        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['category'], int)
        self.assertIsInstance(data['fullDescription'], str)
        self.assertIsInstance(data['freeDelivery'], bool)
        self.assertIsInstance(data['reviews'], int)
        self.assertIsInstance(data['price'], float)
        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['images'], list)
        self.assertIsInstance(data['rating'], float)
        self.assertIsInstance(data['title'], str)
        self.assertIsInstance(data['count'], int)
        self.assertIsInstance(data['date'], str)
        self.assertIsInstance(data['description'], str)


    def test_anonym_basket_serializer(self):
        """Test BasketSerializer for anonymous user"""
        qs = Product.objects.annotate(Count('review'))
        for item in qs:
            item.count_in_basket = 2

        serializer = AnonymBasket(qs, many=True)
        self.assertEqual(len(qs), 2)
        data = serializer.data[0]
        set_should_be = {
            'id', 'category', 'fullDescription', 'freeDelivery',
            'reviews', 'price', 'tags', 'images', 'rating', 'title',
            'count', 'date', 'description'
        }

        self.assertEqual(set(data), set_should_be)

        self.assertIsInstance(data['id'], int)
        self.assertIsInstance(data['category'], int)
        self.assertIsInstance(data['fullDescription'], str)
        self.assertIsInstance(data['freeDelivery'], bool)
        self.assertIsInstance(data['reviews'], int)
        self.assertIsInstance(data['price'], float)
        self.assertIsInstance(data['tags'], list)
        self.assertIsInstance(data['images'], list)
        self.assertIsInstance(data['rating'], float)
        self.assertIsInstance(data['title'], str)
        self.assertIsInstance(data['count'], int)
        self.assertIsInstance(data['date'], str)
        self.assertIsInstance(data['description'], str)
