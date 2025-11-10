from .reservation_repository import ReservationRepository

class ReservationValidator:
    def __init__(self, reservation_repo: ReservationRepository):
        self.reservation_repo = reservation_repo

    def validate(self, user, caravan, start_date, end_date):
        self._is_date_available(caravan, start_date, end_date)
        self._can_user_book(user)
        self._is_caravan_available(caravan)

    def _is_date_available(self, caravan, start_date, end_date):
        # This will call the repository to check for conflicts
        pass

    def _can_user_book(self, user):
        pass

    def _is_caravan_available(self, caravan):
        pass
