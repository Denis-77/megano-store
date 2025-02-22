import os
from datetime import date

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from app_products.models import (
    Product, Review, Image, Specification, Tag, SaleItem, CatalogItem
)
from app_products.serializers import (
    SpecificationSerializer, TagSerializer, ImageSerializer,
    ReviewSerializer, ProductSerializer, SalesSerializer, TagsSerializer
)


class SerializerTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.specification = Specification.objects.create(
            name='Weight',
            value='1kg'
        )
        cls.tag = Tag.objects.create(name='Electronics')
        cls.category = CatalogItem.objects.create(
            title='Test example category'
        )
        cls.user = User.objects.create_user(
            username='TestUser',
            password='123456',
            email='test@example.test'
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
        cls.product.specifications.add(cls.specification)
        cls.product.tags.add(cls.tag)

        cls.image = Image.objects.create(
            src=SimpleUploadedFile('test.png', b'file data'),
            alt='test image',
            product=cls.product
        )
        cls.review = Review.objects.create(
            user=cls.user,
            text='Great product',
            rate=5,
            product=cls.product
        )
        # one more for checking rate calculation
        Review.objects.create(
            user=cls.user,
            text='Great product',
            rate=4,
            product=cls.product
        )
        cls.sale_item = SaleItem.objects.create(
            product=cls.product,
            sale_price=79.99,
            date_from=date.today(),
            date_to=date.today()
        )

    @classmethod
    def tearDownClass(cls):
        """
        Delete test file
        """
        super().tearDownClass()
        path_file = cls.image.src.path

        if os.path.isfile(path_file):
            os.remove(path_file)

    def test_specification_serializer(self):
        """Test specification fields (in serializer)"""
        serializer = SpecificationSerializer(self.specification)
        data = serializer.data
        self.assertEqual(data['name'], 'Weight')
        self.assertEqual(data['value'], '1kg')

    def test_image_serializer(self):
        """Test image fields (in serializer)"""
        serializer = ImageSerializer(self.image)
        data = serializer.data
        self.assertEqual(data['src'], f'/media/images/products/{self.product.id}/test.png')
        self.assertEqual(data['alt'], 'test image')

    def test_review_serializer(self):
        """Test review fields (in serializer)"""
        serializer = ReviewSerializer(self.review)
        data = serializer.data
        self.assertEqual(data['author'], 'TestUser')
        self.assertEqual(data['email'], 'test@example.test')
        self.assertEqual(data['text'], 'Great product')
        self.assertEqual(data['rate'], 5)
        self.assertTrue(data['date'])

    def test_product_serializer(self):
        """Test product fields (in serializer)"""
        serializer = ProductSerializer(self.product)
        data = serializer.data
        set_should_be = {
            'id', 'count', 'date', 'title', 'specifications',
            'tags', 'images', 'reviews', 'price', 'fullDescription',
            'description', 'freeDelivery', 'rating'
        }
        self.assertCountEqual(data, set_should_be)
        self.assertEqual(set(data), set_should_be)

        self.assertEqual(data['count'], 10)
        self.assertTrue(data['date'])
        self.assertEqual(data['title'], 'test_product')
        self.assertEqual(data['specifications'][0], {'name': 'Weight', 'value': '1kg'})
        self.assertEqual(data['tags'][0], {'name': 'Electronics'})
        self.assertEqual(data['images'][0]['alt'], self.image.alt)

        self.assertEqual(set(data['reviews'][0]), {'text', 'author', 'email', 'rate', 'date'})
        self.assertEqual(data['reviews'][0]['text'], self.review.text)

        self.assertEqual(data['price'], 99.99)
        self.assertEqual(data['fullDescription'], 'This is a product description.')
        self.assertEqual(data['description'], 'This is a product description.'[:20] + '...')
        self.assertEqual(data['freeDelivery'], True)
        self.assertEqual(data['rating'], 4.5)

    def test_sales_serializer(self):
        """Sale fields test (in serializer)"""
        serializer = SalesSerializer(self.sale_item)
        data = serializer.data
        self.assertEqual(data['salePrice'], 79.99)
        self.assertTrue(data['dateFrom'])
        self.assertTrue(data['dateTo'])
        self.assertEqual(data['price'], 99.99)

    def test_tags_serializer(self):
        """Tag fields test (in serializer)"""
        serializer = TagsSerializer(self.tag)
        data = serializer.data
        self.assertEqual(data['id'], self.tag.id)
        self.assertEqual(data['name'], 'Electronics')
