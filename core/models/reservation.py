from django.db import models
from .user import User
from .caravan import Caravan

class Reservation(models.Model):
    class ReservationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    caravan = models.ForeignKey(Caravan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=ReservationStatus.choices, default=ReservationStatus.PENDING)
