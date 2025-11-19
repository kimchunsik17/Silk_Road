from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        GUEST = 'GUEST', 'Guest'
        HOST = 'HOST', 'Host'

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.GUEST,
    )
    contact = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
