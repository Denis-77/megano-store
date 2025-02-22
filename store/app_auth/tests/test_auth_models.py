import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from app_auth.models import Profile, Avatar


class ProfileModelsTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='testuser',
            password='12345'
        )
        cls.profile = Profile.objects.create(
            user=cls.user,
            phone=1234567890,
            default_city='City',
            default_address='Street 123',
            default_delivery_type='Courier',
            default_payment_type='Card'
        )
        cls.avatar = Avatar.objects.create(
            profile=cls.profile,
            src=SimpleUploadedFile('test_avatar.png', b'file data')
        )

    @classmethod
    def tearDownClass(cls):
        """Delete test file"""
        super().tearDownClass()
        path_file = cls.avatar.src.path

        if os.path.isfile(path_file):
            os.remove(path_file)


    def test_profile_creation(self):
        """Test Profile creation"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.phone, 1234567890)

    def test_avatar_creation(self):
        """Test Avatar creation"""
        self.assertEqual(self.avatar.src.name, f'images/users/{self.user.id}/test_avatar.png')
        self.assertEqual(self.avatar.profile.user.username, 'testuser')

    def test_update_avatar_file(self):
        """Test update Avatar, where file should be deleted after updating"""
        path = self.avatar.src.path
        self.assertTrue(os.path.exists(path))
        self.avatar.src = SimpleUploadedFile('test_avatar_1.png', b'file data')
        self.avatar.save()
        self.assertFalse(os.path.exists(path))
        self.assertEqual(self.avatar.src.path.split('/')[-1], 'test_avatar_1.png')

    def test_delete_avatar_file(self):
        """Test delete Avatar, where file should be deleted after updating"""

        user = User.objects.create(username='testuser_2', password='12345')
        profile = Profile.objects.create(
            user=user,
            phone=1234567890
        )
        avatar = Avatar.objects.create(
            profile=profile,
            src=SimpleUploadedFile('test_avatar_2.png', b'file data')
        )
        path = avatar.src.path

        self.assertTrue(os.path.exists(path))
        avatar.delete()
        self.assertFalse(os.path.exists(path))
