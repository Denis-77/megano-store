import os

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from app_catalog.models import CatalogItem, Image


class CatalogTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.parent = CatalogItem.objects.create(
            title='Parent Catalog Item'
        )
        cls.child = CatalogItem.objects.create(
            title='Child Catalog Item',
            parent_category=cls.parent
        )

        cls.image = Image.objects.create(
            src=SimpleUploadedFile('test.png', b'file data'),
            alt='test image',
            catalog_item=cls.child
        )

    @classmethod
    def tearDownClass(cls):
        """Delete test file"""
        super().tearDownClass()
        path_file = cls.image.src.path

        if os.path.isfile(path_file):
            os.remove(path_file)

    def test_catalog_item_creation(self):
        """Test to check creation new category object"""
        self.assertEqual(self.child.title, 'Child Catalog Item')

    def test_catalog_item_parent_category(self):
        """Test foreign key"""
        self.assertEqual(self.child.parent_category, self.parent)
        self.assertEqual(self.parent.catalog_item.first(), self.child)

    def test_image_creation(self):
        """Test to check creation new image object"""
        image_qs = Image.objects.filter(catalog_item=self.child)
        self.assertTrue(image_qs.exists(), msg='No images for created product')
        image = image_qs.first()
        self.assertEqual(image.alt, 'test image')

    def test_image_dir_path(self):
        """Test to check path to new image file"""
        expected_path = f'images/catalog_items/test.png'
        self.assertEqual(self.image.src.name, expected_path)
