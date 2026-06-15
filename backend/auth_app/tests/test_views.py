from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationEndpointTests(APITestCase):
    """Test authentication endpoints"""

    def test_register_user(self):
        """Test user registration endpoint"""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'TestPass123!',
            'confirmed_password': 'TestPass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_register_user_password_mismatch(self):
        """Test registration fails with mismatched passwords"""
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'confirmed_password': 'DifferentPass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user(self):
        """Test user login endpoint"""
        # First register a user
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        url = reverse('login')
        data = {
            'email': 'wrong@example.com',
            'password': 'WrongPass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_user(self):
        """Test user logout endpoint"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='TestPass123!'
        )
        
        self.client.force_authenticate(user=user)
        
        url = reverse('logout')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
