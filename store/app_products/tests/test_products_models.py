import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase


from app_products.models import (
    Product, DEFAULT_IMAGE_FOR_PRODUCTS, Image, Review
)
from app_catalog.models import CatalogItem


class ProductTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = CatalogItem.objects.create(
            title='TestCategory'
        )

        cls.product = Product.objects.create(
            title='Test product',
            description='Description of Product',
            price=3.99,
            count=3,
            rating=3.0,
            free_delivery=False,
            category=cls.category
        )

        cls.user = User.objects.create_user(
            username='TestUser',
            password='123456',
            email='test@example.test'
        )

    def test_product_creation(self):
        """
        Test to check creation new product object
        """
        self.assertEqual(self.product.description, 'Description of Product')
        self.assertEqual(self.product.price, 3.99)
        self.assertEqual(self.product.count, 3)
        self.assertEqual(self.product.rating, 3.0)
        self.assertEqual(self.product.free_delivery, False)
        self.assertEqual(self.product.count, 3)
        self.assertEqual(self.product.category, self.category)

    def test_default_image_adding(self):
        """
        Test to check the creation of a default image for a new product with right path to file
        """
        image_qs = Image.objects.filter(product=self.product)
        self.assertTrue(image_qs.exists(), msg='No images for created product')
        image = image_qs.first()
        self.assertEqual(image.src, DEFAULT_IMAGE_FOR_PRODUCTS)
        self.assertEqual(image.alt, 'Empty')

    def test_uploading_and_deleting_file(self):
        """
        Test to check that the default image was deleted after upload,
        that the default image was added, and that the file was deleted
        form directory after deletion.
        Also deletes the test file from the directory in any case.
        """
        path_file = 'images/products/{}/test.png'.format(self.product.id)
        try:
            image = Image.objects.create(
                src=SimpleUploadedFile('test.png', b'file data'),
                alt='test image',
                product=self.product
            )
            self.assertEqual(image.src.name, path_file)

            # check that default image was deleted
            images_qs = Image.objects.filter(product=self.product)
            self.assertEqual(len(images_qs), 1)
            image_from_qs = images_qs.first()
            self.assertEqual(image_from_qs.alt, 'test image')

            # check autocreation default after deleting
            image.delete()
            images_qs = Image.objects.filter(product=self.product)
            self.assertEqual(len(images_qs), 1)
            image_from_qs = images_qs.first()
            self.assertEqual(image_from_qs.alt, 'no images have been added')

            # check deleting file form directory
            image_path = os.path.join(settings.MEDIA_ROOT, path_file)
            self.assertFalse(os.path.isfile(image_path))

        finally:
            abs_path = os.path.join(settings.MEDIA_ROOT, path_file)
            if os.path.isfile(abs_path):
                os.remove(abs_path)

    def test_creation_review(self):
        """
        Test of creating a review and calculating the rating
        :return:
        """
        Review.objects.create(
            text='TestText',
            rate='2',
            user=self.user,
            product=self.product
        )

        review = Review.objects.get(text='TestText')
        self.assertEqual(review.rate, 2)
        Review.objects.create(
            text='TestText',
            rate='4',
            user=self.user,
            product=self.product
        )
        self.assertEqual(self.product.rating, 3)
