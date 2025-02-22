import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from app_auth.models import Profile, Avatar


class ProfileViewSetTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='testuser',
            first_name='TestUserName',
            email='test@email.example'
        )
        cls.user.set_password('myPassword1234')
        cls.user.save()
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

        cls.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        """Delete test file"""
        super().tearDownClass()
        path_file = cls.avatar.src.path

        if os.path.isfile(path_file):
            os.remove(path_file)


    def test_sign_up_view(self):
        """Test sign-up view"""
        # There is a lot of strange things because of frontend
        bad_data = {
            '{"name":"test_name","username":"test_user","password":"short"}': ''
        }
        response = self.client.post(
            '/api/sign-up',
            data=json.dumps(bad_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        normal_data = {
            '{"name":"test_name","username":"test_user","password":"normal123123"}': ''
        }
        response = self.client.post(
            '/api/sign-up',
            data=json.dumps(normal_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_qs = User.objects.filter(username='test_user')
        self.assertTrue(user_qs.exists())
        profile_qs = Profile.objects.filter(user=user_qs.first())
        self.assertTrue(profile_qs.exists())

        data_with_duplicate = {
            '{"name":"test_2_name","username":"test_user","password":"normal444123"}': ''
        }
        response = self.client.post(
            '/api/sign-up',
            data=json.dumps(data_with_duplicate),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


    def test_sign_in_view(self):
        """Test sign-in, sign-out view"""
        self.assertFalse('_auth_user_id' in self.client.session)

        data_in = {
            'username': 'testuser',
            'password': 'myPassword1234'
        }
        response = self.client.post(
            '/api/sign-in',
            data=json.dumps(data_in),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('_auth_user_id' in self.client.session)

        response = self.client.post(
            '/api/sign-out'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse('_auth_user_id' in self.client.session)


    def test_profile_getting_view(self):
        """Test profile(get) view"""
        self.client.login(username='testuser', password='myPassword1234')

        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data['first_name'], 'TestUserName')
        self.assertEqual(data['email'], 'test@email.example')
        self.assertEqual(data['phone'], '1234567890')
        self.assertEqual(data['avatar']['src'].split('/')[-1], 'test_avatar.png')
        self.assertEqual(data['avatar']['alt'], 'image')

        self.assertEqual(data['fullName'], 'TestUserName')


    def test_profile_update_view(self):
        """Test profile update view"""
        self.assertFalse('_auth_user_id' in self.client.session)
        self.client.login(
            username='testuser',
            password='myPassword1234'
        )
        profile = Profile.objects.get(
            user=self.user
        )
        self.assertEqual(profile.user.first_name, 'TestUserName')
        self.assertEqual(profile.user.email, 'test@email.example')
        self.assertEqual(profile.phone, 1234567890)

        data = {
            'fullName': 'Annoying Orange',
            'email': 'no-reply@exampre.com',
            'phone': '88002000600'
        }
        response = self.client.post(
            '/api/profile',
            data=json.dumps(data),
            content_type='application/json'
        )
        profile = Profile.objects.get(
            user=self.user
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.user.first_name, 'Annoying Orange')
        self.assertEqual(profile.user.email, 'no-reply@exampre.com')
        self.assertEqual(profile.phone, 88002000600)


    def test_change_password_view(self):
        """Test change password view"""
        self.assertFalse('_auth_user_id' in self.client.session)

        data_in_old = {
            'username': 'testuser',
            'password': 'myPassword1234'
        }
        response = self.client.post(
            '/api/sign-in',
            data=json.dumps(data_in_old),
            content_type='application/json'
        )
        self.assertTrue('_auth_user_id' in self.client.session)

        data_change = {
            'currentPassword': 'myPassword1234',
            'newPassword': 'newPassword1234'
        }
        response = self.client.post(
            '/api/profile/password',
            data=json.dumps(data_change),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
        self.assertFalse('_auth_user_id' in self.client.session)

        response = self.client.post(
            '/api/sign-in',
            data=json.dumps(data_in_old),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        data_in_new = {
            'username': 'testuser',
            'password': 'newPassword1234'
        }
        response = self.client.post(
            '/api/sign-in',
            data=json.dumps(data_in_new),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data_change_back = {
            'currentPassword': 'newPassword1234',
            'newPassword': 'myPassword1234'
        }
        response = self.client.post(
            '/api/profile/password',
            data=json.dumps(data_change_back),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_change_avatar_view(self):
        """Test change avatar view"""
        self.assertFalse('_auth_user_id' in self.client.session)
        self.client.login(
            username='testuser',
            password='myPassword1234'
        )
        profile = Profile.objects.get(
            user=self.user
        )
        self.assertTrue(
            profile.avatar.src.name.split('/')[-1] == 'test_avatar.png'
        )
        file = SimpleUploadedFile('new_test_avatar.png', b'file data')
        response = self.client.post(
            '/api/profile/avatar', {'avatar': file}, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = Profile.objects.get(
            user=self.user
        )

        self.assertFalse(
            profile.avatar.src.name.split('/')[-1] == 'test_avatar.png'
        )
        self.assertTrue(
            profile.avatar.src.name.split('/')[-1] == 'new_test_avatar.png'
        )
        prev_file = SimpleUploadedFile('test_avatar.png', b'file data')
        response = self.client.post(
            '/api/profile/avatar', {'avatar': prev_file}, format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
