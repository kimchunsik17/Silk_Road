from core.models import Caravan, Reservation

class CaravanRepository:
    def get_by_id(self, caravan_id: int) -> Caravan:
        return Caravan.objects.get(pk=caravan_id)

    def find_available(self, start_date, end_date, capacity: int):
        conflicting_reservations = Reservation.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        ).values_list('caravan_id', flat=True)

        return Caravan.objects.exclude(
            id__in=conflicting_reservations
        ).filter(
            capacity__gte=capacity,
            status=Caravan.CaravanStatus.AVAILABLE
        )
