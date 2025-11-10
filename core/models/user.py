from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        HOST = 'HOST', 'Host'
        GUEST = 'GUEST', 'Guest'

    user_type = models.CharField(max_length=5, choices=UserType.choices)
    is_verified = models.BooleanField(default=False)
