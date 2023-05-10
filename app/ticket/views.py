'''
Views for the ticket APIs.
'''
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ticket
from ticket import serializers


class TicketViewSet(viewsets.ModelViewSet):
    '''View for manage ticket APIs.'''
    serializer_class = serializers.TicketDetailSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ticket.objects.all()

    def get_queryset(self):
        '''Return objects for the current authenticated user only.'''
        query = self.queryset.filter(owner=self.request.user)
        return query.order_by('-created_at')

    def get_serializer_class(self):
        '''Return appropriate serializer class.'''
        if self.action == 'list':
            return serializers.TicketSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''Create a new ticket.'''
        serializer.save(owner=self.request.user)
