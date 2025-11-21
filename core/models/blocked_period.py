from django.db import models
from .caravan import Caravan

class BlockedPeriod(models.Model):
    caravan = models.ForeignKey(Caravan, on_delete=models.CASCADE, related_name='blocked_periods')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # Ensure no overlapping blocked periods for the same caravan
        constraints = [
            models.UniqueConstraint(
                fields=['caravan', 'start_date', 'end_date'],
                name='unique_blocked_period_for_caravan'
            )
        ]

    def __str__(self):
        return f"Blocked: {self.caravan.name} from {self.start_date} to {self.end_date}"
