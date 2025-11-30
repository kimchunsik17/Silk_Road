from django.db import models
from .user import User

class PaymentMethod(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    card_brand = models.CharField(max_length=50)
    card_last_four = models.CharField(max_length=4)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.card_brand} ending in {self.card_last_four}"
