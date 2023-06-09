'''
URL mapping for ticket app.
'''
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from ticket import views

router = DefaultRouter()
router.register('ticket', views.TicketViewSet)
router.register('event', views.EventViewSet)

app_name = 'ticket'

urlpatterns = [
    path('', include(router.urls)),
]
