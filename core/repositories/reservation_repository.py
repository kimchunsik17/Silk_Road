from django.db.models import Q
from core.models import Reservation

class ReservationRepository:
    def check_conflict(self, caravan_id: int, start_date, end_date):
        return Reservation.objects.filter(
            caravan_id=caravan_id,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()
