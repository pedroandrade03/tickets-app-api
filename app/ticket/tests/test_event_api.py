'''
Tests for the events APIs.
'''
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event
from ticket.serializers import EventSerializer

EVENTS_URL = reverse('ticket:event-list')


def create_user(**params):
    '''Helper function to create new user.'''
    return get_user_model().objects.create_user(**params)


def PublicEventsApiTests(TestCase):
    '''Test the publicly available events API.'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test that login is required for retrieving events.'''
        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def PrivateEventsApiTests(TestCase):
    '''Test the authorized user events API.'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass1')
        self.client.force_authenticate(self.user)

    def test_retrive_events(self):
        '''Test retrieving a list of events.'''
        Event.objects.create(
            owner=self.user,
            name='Test event',
            description='Test description',
            started_at=timezone.now(),
            duration_hours=10,
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('-created_at')
        serializer = EventSerializer(events, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_event_limited_to_owner(self):
        '''Test retrieving events for owner.'''
        user2 = create_user(email='user2@example.com', password='testpass')
        Event.objects.create(
            owner=user2,
            name='Test event',
            description='Test description',
            started_at=timezone.now(),
            duration_hours=10,
        )
        event = Event.objects.create(
            owner=self.user,
            name='Test event',
            description='Test description',
            started_at=timezone.now(),
            duration_hours=10,
        )

        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], event.name)
        self.assertEqual(res.data[0]['id'], event.id)
