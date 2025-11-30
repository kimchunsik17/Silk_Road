from django.db import models
from .reservation import Reservation

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Reservation {self.reservation.id}"
