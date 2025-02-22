from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from app_products.models import Product, Review, SaleItem, Tag, CatalogItem


class ProductViewSetTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = '123456'

        cls.user = User.objects.create_user(
            username='TestUser',
            email='email@for.example',
            password=cls.password
        )

        cls.category = CatalogItem.objects.create(
            title='Test example category'
        )

        cls.product = Product.objects.create(
            price=99.99,
            count=10,
            title='test_product',
            description='This is a product description.',
            free_delivery=True,
            rating=4.5,
            category=cls.category
        )

        cls.sale_items = [SaleItem.objects.create(
            product=cls.product,
            sale_price=sale_num + 1,
            date_from=date.today(),
            date_to=date.today()
        ) for sale_num in range(5)]

        for number in range(5):
            Tag.objects.create(name=f'Tag #{number + 1}')

        cls.client = APIClient()

    def test_product_view_get(self):
        """Test product(get) view"""

        response = self.client.get(f'/api/product/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        set_should_be = {
            'id', 'count', 'date', 'title', 'specifications',
            'tags', 'images', 'reviews', 'price', 'fullDescription',
            'description', 'freeDelivery', 'rating'
        }
        self.assertEqual(set(response.data), set_should_be)
        self.assertEqual(response.data['title'], self.product.title)
        self.assertIsInstance(response.data['specifications'], list)
        self.assertIsInstance(response.data['tags'], list)
        self.assertIsInstance(response.data['images'], list)
        self.assertIsInstance(response.data['reviews'], list)

    def test_create_review_authenticated(self):
        """Test creation(post) review view for authenticated user"""

        self.client.login(username=self.user.username, password=self.password)

        data = {'text': 'Great product!', 'rate': 5}
        response = self.client.post(reverse('make_review', kwargs={'pk': self.product.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().text, 'Great product!')
        self.assertEqual(Review.objects.first().rate, 5)

        data = {'text': 'Not so good', 'rate': 3}
        response = self.client.post(reverse('make_review', kwargs={'pk': self.product.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(Review.objects.get(text='Not so good').rate, 3)
        # checking rating counter
        self.assertEqual(Product.objects.get(pk=self.product.id).rating, 4)

    def test_create_review_unauthenticated(self):
        """Test creation(post) review view for unauthenticated user"""
        data = {'text': 'Great product!', 'rate': 5}
        response = self.client.post(reverse('make_review', kwargs={'pk': self.product.id}), data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(Review.objects.count(), 0)

    def test_list_sales(self):
        """Test sales view with pagination"""
        response = self.client.get('/api/sales/?currentPage=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 4)  # According to the pagination page_size in views
        response = self.client.get('/api/sales/?currentPage=2')
        # Entire sales 5 made  - 4 in first
        self.assertEqual(len(response.data['items']), 1)

    def test_list_tags(self):
        """Test tags view"""
        response = self.client.get(reverse('tags'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
