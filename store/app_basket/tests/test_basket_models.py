from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from app_basket.models import BasketItem
from app_products.models import Product
from app_catalog.models import CatalogItem


class BasketModelsTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='TestUser', password='12345'
        )
        cls.category = CatalogItem.objects.create(
            title='CatalogItemExample'
        )
        cls.product = Product.objects.create(
            title='Product for tests # 1',
            description='Description of product # 1 for test',
            price=1.99,
            count=3,
            rating=5,
            category=cls.category
        )
        cls.basket = BasketItem.objects.create(
            user=cls.user,
            product=cls.product,
            count=2
        )


    def test_basket_creation(self):
        """Test creation basket"""
        self.assertEqual(self.basket.user.username, 'TestUser')
        self.assertEqual(self.basket.product.title, 'Product for tests # 1')
        self.assertEqual(self.basket.count, 2)
