'''
Serializers for Ticket APIs
'''
from rest_framework import serializers

from core.models import Ticket, Event


class TicketSerializer(serializers.ModelSerializer):
    '''Serializer for ticket objects.'''

    class Meta:
        model = Ticket
        fields = ('id', 'event', 'price', 'paid', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'paid_at')


class TicketDetailSerializer(TicketSerializer):
    '''Serializer for ticket detail objects.'''

    class Meta(TicketSerializer.Meta):
        fields = TicketSerializer.Meta.fields + ('paid_at',)


class EventSerializer(serializers.ModelSerializer):
    '''Serializer for event objects.'''
    class Meta:
        model = Event
        fields = (
            'id',
            'owner',
            'name',
            'description',
            'duration_hours',
            'started_at',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
