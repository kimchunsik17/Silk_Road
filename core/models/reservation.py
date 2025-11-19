from django.db import models
from .user import User
from .caravan import Caravan

class Reservation(models.Model):
    class ReservationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    caravan = models.ForeignKey(Caravan, on_delete=models.CASCADE, related_name='reservations')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
    )

    def __str__(self):
        return f"Reservation for {self.caravan.name} by {self.guest.username}"
