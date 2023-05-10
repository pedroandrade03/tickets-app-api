'''
Tests for ticket APIs.
'''
from decimal import Decimal

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ticket, Event

from ticket.serializers import (
    TicketSerializer,
    TicketDetailSerializer,
)

TICKET_URL = reverse('ticket:ticket-list')


def detail_url(ticket_id):
    '''Create and return ticket detail URL.'''
    return reverse('ticket:ticket-detail', args=[ticket_id])


def create_event(user, **params):
    '''Create and return a new event.'''
    defaults = {
        'name': 'Test event',
        'description': 'Test description',
        'started_at': timezone.now(),
        'duration_hours': 5,
    }
    defaults.update(params)

    return Event.objects.create(owner=user, **defaults)


def create_ticket(user, event, **params):
    '''Create and return a new ticket.'''
    defaults = {
        'price': Decimal('10.00'),
    }
    defaults.update(params)

    return Ticket.objects.create(owner=user, event=event, **defaults)


def create_user(**params):
    '''Create and return a new user.'''
    return get_user_model().objects.create_user(**params)


class PublicTicketAPITests(TestCase):
    '''Test unauthenticated API requests.'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test auth is required to call API.'''
        res = self.client.get(TICKET_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTicketAPITests(TestCase):
    '''Test authenticated API requests.'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass1')
        self.client.force_authenticate(self.user)

    def test_retrive_tickets(self):
        '''Test retrieving a list of tickets.'''
        event = create_event(user=self.user)
        create_ticket(user=self.user, event=event)

        res = self.client.get(TICKET_URL)

        tickets = Ticket.objects.filter(event=event).order_by('-created_at')
        serializer = TicketSerializer(tickets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tickets_limited_to_user(self):
        '''Test retrieving tickets for user.'''
        other_user = create_user(email='other@examp.com', password='testpass')
        event = create_event(user=self.user)
        create_ticket(user=other_user, event=event)
        create_ticket(user=self.user, event=event)

        res = self.client.get(TICKET_URL)

        tickets = Ticket.objects.filter(
            event=event,
            owner=self.user
        ).order_by('-created_at')
        serializer = TicketSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_ticket_detail(self):
        '''Test viewing a ticket detail.'''
        ticket = create_ticket(
            user=self.user,
            event=create_event(user=self.user)
        )

        url = detail_url(ticket.id)
        res = self.client.get(url)

        serializer = TicketDetailSerializer(ticket)
        self.assertEqual(res.data, serializer.data)

    def test_create_ticket(self):
        '''Test creating a new ticket.'''
        payload = {
            'event': create_event(user=self.user).id,
            'price': 5.00,
            'paid': False,
        }
        res = self.client.post(TICKET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ticket = Ticket.objects.get(id=res.data['id'])
        for key, value in payload.items():
            if key == 'event':
                self.assertEqual(value, ticket.event.id)
            else:
                self.assertEqual(value, getattr(ticket, key))
        self.assertEqual(ticket.owner, self.user)

    def test_parcial_update_ticket(self):
        '''Test partial update of a ticket.'''
        ticket = create_ticket(
            user=self.user,
            event=create_event(user=self.user),
            price=5.00
            )
        payload = {'price': 10.00}

        url = detail_url(ticket.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertEqual(ticket.price, Decimal('10.00'))
        self.assertEqual(ticket.owner, self.user)
        self.assertEqual(ticket.event.owner, self.user)

    def test_full_update_ticket(self):
        '''Test full update of a ticket.'''
        ticket = create_ticket(
            user=self.user,
            event=create_event(user=self.user),
            price=5.00,
            paid=False
        )
        payload = {
            'event': create_event(user=self.user).id,
            'price': 10.00,
            'paid': True,
        }

        url = detail_url(ticket.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        for key, value in payload.items():
            if key == 'event':
                self.assertEqual(value, ticket.event.id)
            else:
                self.assertEqual(value, getattr(ticket, key))
        self.assertEqual(ticket.owner, self.user)
        