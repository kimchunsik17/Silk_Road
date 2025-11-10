from django.db import models
from .user import User

class Caravan(models.Model):
    class CaravanStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        RESERVED = 'RESERVED', 'Reserved'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    host = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    amenities = models.JSONField(default=list)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=11, choices=CaravanStatus.choices, default=CaravanStatus.AVAILABLE)
