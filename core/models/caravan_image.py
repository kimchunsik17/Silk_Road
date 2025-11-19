from django.db import models
from .caravan import Caravan

class CaravanImage(models.Model):
    caravan = models.ForeignKey(Caravan, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='caravan_images/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.caravan.name}"
