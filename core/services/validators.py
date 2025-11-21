from core.models import Caravan, User, BlockedPeriod
from core.exceptions import ReservationConflictError, InsufficientPermissionsError
from core.repositories.reservation_repository import ReservationRepository
from django.db.models import Q

class ReservationValidator:
    def __init__(self, reservation_repo: ReservationRepository):
        self.reservation_repo = reservation_repo

    def validate(self, user, caravan, start_date, end_date):
        self._is_caravan_available(caravan)
        self._can_user_book(user)
        self._is_date_available(caravan, start_date, end_date)

    def _is_date_available(self, caravan, start_date, end_date):
        # Check for conflicts with existing reservations
        if self.reservation_repo.check_conflict(caravan.id, start_date, end_date):
            raise ReservationConflictError("Caravan is not available for the selected dates due to an existing reservation.")

        # Check for conflicts with blocked periods
        blocked_periods_conflict = BlockedPeriod.objects.filter(
            Q(caravan=caravan) &
            Q(start_date__lte=end_date) & 
            Q(end_date__gte=start_date)
        ).exists()

        if blocked_periods_conflict:
            raise ReservationConflictError("Caravan is not available for the selected dates due to a blocked period.")

    def _can_user_book(self, user):
        if user.user_type != User.UserType.GUEST:
            raise InsufficientPermissionsError("Only GUEST users can book a caravan.")

    def _is_caravan_available(self, caravan):
        if caravan.status != Caravan.CaravanStatus.AVAILABLE:
            raise ReservationConflictError("Caravan is not available for booking.")
