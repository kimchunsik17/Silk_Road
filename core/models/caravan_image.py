import os
import uuid
from django.db import models
from .caravan import Caravan

def caravan_image_upload_path(instance, filename):
    """
    Generates a unique filename for the uploaded image using UUID.
    Path: caravan_images/<uuid>.<ext>
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return os.path.join('caravan_images', new_filename)

class CaravanImage(models.Model):
    caravan = models.ForeignKey(Caravan, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=caravan_image_upload_path)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.caravan.name}"
