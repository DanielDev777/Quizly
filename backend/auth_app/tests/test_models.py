from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

User = get_user_model()

class UserModelTests(TestCase):
    """Test cases for Custom User model"""

    def test_create_user_with_email(self):
        """Test creating a user with email is successful"""
        email = 'test@example.com'
        password = 'TestPass123!'
        user = User.objects.create_user(
            email=email,
            username='testuser',
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_email_is_unique(self):
        """Test that email must be unique"""
        email = 'test@example.com'
        User.objects.create_user(
            email=email,
            username='user1',
            password='TestPass123!'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=email,
                username='user2',
                password='TestPass123!'
            )

    def test_user_string_representation(self):
        """Test the user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )

        self.assertEqual(str(user), 'test@example.com')