import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from app_auth.models import Profile, Avatar
from app_auth.serializers import (
    UserSerializer, ProfileSerializer, CreateUserSerializer
)


class ProfileSerializersTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='testuser',
            password='12345',
            first_name='TestUserName',
            email='test@email.example'
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


    def test_user_serializer(self):
        """Test user fields (in serializer)"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        set_should_be = {
            'first_name', 'email', 'phone', 'avatar', 'fullName'
        }
        self.assertEqual(set(data), set_should_be)
        self.assertEqual(data['first_name'], 'TestUserName')
        self.assertEqual(data['email'], 'test@email.example')
        self.assertEqual(data['phone'], '1234567890')
        self.assertIsInstance(data['avatar'], dict)
        self.assertEqual(data['fullName'], 'TestUserName')

    def test_profile_serializer(self):
        """Test profile fields (in serializer)"""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        set_should_be = {
            'user', 'phone', 'avatar'
        }
        self.assertEqual(set(data), set_should_be)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['phone'], 1234567890)
        self.assertIsInstance(data['avatar'], dict)

    def test_creation_user_serializer(self):
        """Test user creation"""
        correct_data = {
            "first_name": "TestName",
            "username": "test1test",
            "password": "password123"
        }
        serializer = CreateUserSerializer(data=correct_data)
        self.assertTrue(serializer.is_valid())

        short_pass_data = {
            "first_name": "TestName_2",
            "username": "test2test",
            "password": "short"
        }
        serializer = CreateUserSerializer(data=short_pass_data)
        self.assertFalse(serializer.is_valid())

        only_letters_pass_data = {
            "first_name": "TestName_2",
            "username": "test2test",
            "password": "PasswordWithOnlyLetters"
        }
        serializer = CreateUserSerializer(data=only_letters_pass_data)
        self.assertFalse(serializer.is_valid())

        only_digits_pass_data = {
            "first_name": "TestName_2",
            "username": "test2test",
            "password": "123456789012345"
        }
        serializer = CreateUserSerializer(data=only_digits_pass_data)
        self.assertFalse(serializer.is_valid())
