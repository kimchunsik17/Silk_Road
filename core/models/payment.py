from django.db import models
from .reservation import Reservation

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=6, choices=PaymentStatus.choices)
    paid_at = models.DateTimeField(null=True, blank=True)
