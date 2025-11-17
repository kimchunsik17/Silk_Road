from django.urls import path
from .views import create_reservation_view

urlpatterns = [
    path('reservations/', create_reservation_view, name='create-reservation-api'),
]
