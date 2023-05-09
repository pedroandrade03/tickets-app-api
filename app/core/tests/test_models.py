"""
Test for models
"""
from decimal import Decimal

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@exemple.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['Test3@EXAMPLE.COM', 'Test3@example.com'],
            ['Test4@example.COM', 'Test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'test123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_error(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        '''Test creating a superuser.'''
        user = get_user_model().objects.create_superuser(
            'test@exemple.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_event(self):
        '''Test creating an event.'''
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123',
        )

        event = models.Event.objects.create(
            name='Pool Party',
            description='Pool Party',
            started_at=timezone.now(),
            duration_hours=5,
            owner=user,
        )
        self.assertEqual(str(event), event.name)

    def test_create_ticket(self):
        '''Test creating a recipe.'''
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123',
        )

        event = models.Event.objects.create(
            name='Pool Party',
            description='Pool Party February 2021',
            started_at=timezone.now(),
            duration_hours=Decimal('5.00'),
            owner=user,
        )

        ticket = models.Ticket.objects.create(
            event=event,
            owner=user,
            price=Decimal('10.00'),
        )

        self.assertEqual(str(ticket), event.name)
        self.assertEqual(ticket.price, Decimal('10.00'))
        ticket.pay()
        self.assertTrue(ticket.paid)
        self.assertIsNotNone(ticket.paid_at)
