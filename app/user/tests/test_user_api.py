'''
Tests for user API.
'''
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    '''Create and return a new user.'''
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    '''Test the public users API.'''

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        '''Test creating user is successful.'''
        payload = {
            'email': 'test@exemple.com',
            'password': 'test12345678',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        '''Test creating user that already exists fails.'''
        payload = {
            'email': 'test@exemple.com',
            'password': 'test123',
            'name': 'Test User'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_erro(self):
        '''Test that password must be more than 8 characters.'''
        payload = {
            'email': 'test@exemple.com',
            'password': 'test123',
            'name': 'Test User'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test that a token is created for the user.'''
        userdetails = {
            'email': 'test@exemple.com',
            'password': 'test123',
            'name': 'Test User'
        }
        create_user(**userdetails)

        payload = {
            'email': userdetails['email'],
            'password': userdetails['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        '''Test that token is not created if invalid credentials are given.'''
        userdetails = {
            'email': 'test@exemple.com',
            'password': 'test123',
            'name': 'Test User'
        }
        create_user(**userdetails)

        payload = {
            'email': 'wrong',
            'password': 'wrong'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        '''Test that token is not created if user doesn't exist.'''
        userdetails = {
            'email': 'test@exemple.com',
            'password': 'test123',
            'name': 'Test User'
        }
        create_user(**userdetails)

        payload = {
            'email': 'wrong',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        '''Test that authentication is required for users.'''
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    '''Test API requests that require authentication.'''

    def setUp(self):
        self.user = create_user(
            email='test@exemple.com',
            password='test123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def teste_retrieve_profile_success(self):
        '''Test retrieving profile for logged in used.'''
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        '''Test that POST is not allowed on the me url.'''
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)








