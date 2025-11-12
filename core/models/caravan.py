from django.db import models
from .user import User

class Caravan(models.Model):
    class CaravanStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        RESERVED = 'RESERVED', 'Reserved'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caravans')
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField(default=list)
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=CaravanStatus.choices,
        default=CaravanStatus.AVAILABLE,
    )

    def __str__(self):
        return self.name
