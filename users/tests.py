from django.test import TestCase
from django.contrib.auth import get_user_model


class UserCreationTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'name': 'Test User',
            'mobile_number': '9876543210'
        }

    def test_user_creation(self):
        user = self.user_model.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.mobile_number, self.user_data['mobile_number'])

    def test_duplicate_email(self):
        self.user_model.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(**self.user_data)

    def test_invalid_mobile_number(self):
        invalid_data = self.user_data.copy()
        invalid_data['mobile_number'] = '1234567890'
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(**invalid_data)

    def test_without_email(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = None
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(**invalid_data)

    def test_without_mobile_number(self):
        invalid_data = self.user_data.copy()
        invalid_data['mobile_number'] = None
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(**invalid_data)

    def test_without_name(self):
        invalid_data = self.user_data.copy()
        invalid_data['name'] = None
        with self.assertRaises(Exception):
            self.user_model.objects.create_user(**invalid_data)