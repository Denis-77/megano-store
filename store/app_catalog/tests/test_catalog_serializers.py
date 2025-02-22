import os
from types import NoneType

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Count, Min
from rest_framework.test import APITestCase

from app_catalog.models import Image, CatalogItem
from app_products.models import Product
from app_catalog.serializers import (
    ImageSerializer, CatalogItemSerializer, ProductSerializerForCatalog,
    BannerSerializer
)


class SerializerTestCase(APITestCase):
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
        cls.image_child_1 = Image.objects.create(
            src=SimpleUploadedFile('test_2.png', b'file data'),
            alt='test image',
            catalog_item=cls.child_1
        )
        cls.image_child_2 = Image.objects.create(
            src=SimpleUploadedFile('test_3.png', b'file data'),
            alt='test image',
            catalog_item=cls.child_2
        )

    @classmethod
    def tearDownClass(cls):
        """Delete test file"""
        super().tearDownClass()

        path_file = cls.image_parent.src.path
        if os.path.isfile(path_file):
            os.remove(path_file)

        path_file = cls.image_child_1.src.path
        if os.path.isfile(path_file):
            os.remove(path_file)

        path_file = cls.image_child_2.src.path
        if os.path.isfile(path_file):
            os.remove(path_file)

    def test_image_serializer(self):
        """Test image fields (in serializer)"""
        serializer = ImageSerializer(self.image_parent)
        data = serializer.data
        self.assertEqual(data['src'], f'/media/images/catalog_items/test_1.png')
        self.assertEqual(data['alt'], 'test image')

    def test_catalog_item_serializer(self):
        """Test category fields (in serializer)"""
        serializer = CatalogItemSerializer(self.parent)
        data = serializer.data
        set_should_be = {
            'id', 'title', 'image', 'subcategories'
        }
        self.assertCountEqual(data, set_should_be)
        self.assertEqual(set(data), set_should_be)

        self.assertEqual(data['title'], 'Parent Catalog Item')
        self.assertEqual(data['image']['alt'], 'test image')

        self.assertIsInstance(data['subcategories'], list)
        self.assertEqual(len(data['subcategories']), 2)
        self.assertEqual(set(data['subcategories'][0]), set_should_be)


    def test_product_for_catalog_serializer(self):
        """Test ProductForCatalogSerializer"""
        for product_num in range(1, 11):
            Product.objects.create(
                title=f'Product for tests #{product_num}',
                description=f'Description of product #{product_num} for test',
                price=product_num + 0.99,
                count=product_num,
                rating=5,
                category=[self.child_1, self.child_2][product_num % 2]
            )
        serializer = ProductSerializerForCatalog(Product.objects.all().annotate(Count('review')), many=True)
        data = serializer.data
        set_should_be = {
            'id', 'price', 'count', 'date', 'title',
            'description', 'freeDelivery', 'rating',
            'tags', 'images', 'reviews', 'category',
            'fullDescription'
        }

        self.assertEqual(len(data), 10)
        self.assertEqual(set(data[0]), set_should_be)

        self.assertIsInstance(data[0]['id'], int)
        self.assertIsInstance(data[0]['price'], float)
        self.assertIsInstance(data[0]['count'], int)
        self.assertIsInstance(data[0]['date'], str)
        self.assertIsInstance(data[0]['title'], str)
        self.assertIsInstance(data[0]['description'], str)
        self.assertIsInstance(data[0]['freeDelivery'], bool)
        self.assertIsInstance(data[0]['rating'], float)
        self.assertIsInstance(data[0]['tags'], list)
        self.assertIsInstance(data[0]['images'], list)
        self.assertIsInstance(data[0]['reviews'], int)
        self.assertIsInstance(data[0]['category'], int)
        self.assertIsInstance(data[0]['fullDescription'], str)


    def test_banner_serializer(self):
        """Test banner fields (in serializer)"""
        queryset = (
            CatalogItem.objects
            .annotate(Min('product__price'))
        )
        serializer = BannerSerializer(queryset, many=True)
        data = serializer.data
        set_should_be = {
            'id', 'title', 'images', 'category',
            'price'
        }

        self.assertEqual(len(data), 3)
        self.assertEqual(set(data[0]), set_should_be)

        self.assertEqual(data[0]['title'], 'Parent Catalog Item')
        self.assertEqual(data[0]['images'][0]['alt'], 'test image')
        self.assertIsInstance(data[0]['category'], int)
        self.assertIsInstance(data[0]['price'], float|NoneType)
