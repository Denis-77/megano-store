import os

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from app_catalog.models import CatalogItem, Image
from app_products.models import Product


class CatalogViewSetTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.parent = CatalogItem.objects.create(
            title='Parent Catalog Item'
        )
        cls.child_1 = CatalogItem.objects.create(
            title='Child Catalog Item 1',
            parent_category=cls.parent
        )
        cls.child_2 = CatalogItem.objects.create(
            title='Child Catalog Item 2',
            parent_category=cls.parent
        )

        cls.image_parent = Image.objects.create(
            src=SimpleUploadedFile('test_1.png', b'file data'),
            alt='test image',
            catalog_item=cls.parent
        )

        cls.client = APIClient()

        for product_num in range(1, 11):
            Product.objects.create(
                title=f'Product for tests #{product_num}',
                description=f'Description of product #{product_num} for test',
                price=product_num + 0.99,
                count=product_num,
                rating=5,
                category=[cls.child_1, cls.child_2][product_num % 2]
            )

    @classmethod
    def tearDownClass(cls):
        """Delete test file"""
        super().tearDownClass()

        path_file = cls.image_parent.src.path
        if os.path.isfile(path_file):
            os.remove(path_file)

    def test_categories_view(self):
        """Test categories view"""

        response = self.client.get('/api/categories/')
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        set_should_be = {
            'id', 'title', 'subcategories', 'image'
        }

        # return 1, only top category
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0]), set_should_be)

        self.assertEqual(data[0]['title'], self.parent.title)
        self.assertEqual(data[0]['image']['alt'], self.parent.item_image.alt)
        self.assertIsInstance(data[0]['subcategories'], list)
        self.assertEqual(len(data[0]['subcategories']), 2)
        self.assertEqual(set(data[0]['subcategories'][0]), set_should_be)

    def test_limited_products_view(self):
        """Test of limited product list"""

        response = self.client.get('/api/products/limited/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        # Limited are products the quantity of which is from 1 to 3
        self.assertEqual(len(data), 3)
        product = data[0]
        set_should_be_product = {
            'id', 'title', 'price', 'rating', 'description', 'category',
            'freeDelivery', 'fullDescription', 'reviews', 'date', 'tags',
            'images', 'count'
        }

        self.assertEqual(set(product), set_should_be_product)
        self.assertIsInstance(product['tags'], list)
        self.assertIsInstance(product['images'], list)

    def test_products_list_view(self):
        """Test of product list, filters, sorting and pagination"""

        response = self.client.get('/api/catalog/', data={
            'filter[name]': '',
            'filter[minPrice]': 4,
            'filter[maxPrice]': 5,
            'filter[freeDelivery]': 'false',
            'filter[available]': 'true',
            'sort': 'date',
            'sortType': '',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        set_should_be = {
            'items', 'currentPage', 'lastPage'
        }
        data = response.data

        self.assertEqual(set(data), set_should_be)
        self.assertIsInstance(data['items'], list)

        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['title'], 'Product for tests #4')

        response = self.client.get('/api/catalog/', data={
            'filter[name]': '6',
            'filter[minPrice]': 1,
            'filter[maxPrice]': 11,
            'filter[freeDelivery]': 'false',
            'filter[available]': 'true',
            'sort': 'date',
            'sortType': '',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['title'], 'Product for tests #6')

        response = self.client.get('/api/catalog/', data={
            'filter[name]': '',
            'filter[minPrice]': 1,
            'filter[maxPrice]': 11,
            'filter[freeDelivery]': 'false',
            'filter[available]': 'true',
            'sort': 'price',
            'sortType': 'dec',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        # pagination
        self.assertEqual(len(data['items']), 4) # pagination settings
        self.assertEqual(data['currentPage'], 1)
        self.assertEqual(data['lastPage'], 3)

        self.assertEqual(data['items'][0]['title'], 'Product for tests #10')

    def test_popular_products_view(self):
        """Test of popular product list"""

        response = self.client.get('/api/products/popular/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 8)
        product = data[0]
        set_should_be_product = {
            'id', 'title', 'price', 'rating', 'description', 'category',
            'freeDelivery', 'fullDescription', 'reviews', 'date', 'tags',
            'images', 'count'
        }

        self.assertEqual(set(product), set_should_be_product)
        self.assertIsInstance(product['tags'], list)
        self.assertIsInstance(product['images'], list)

    def test_banners_view(self):
        """Test of banners view"""

        response = self.client.get('/api/banners/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIsInstance(data, list)
        product = data[0]
        set_should_be_product = {
            'id', 'title', 'price', 'category', 'images'
        }

        self.assertEqual(set(product), set_should_be_product)
        self.assertEqual(product['category'], product['id'])
        self.assertIsInstance(product['images'], list)
