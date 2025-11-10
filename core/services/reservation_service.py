from core.models import User, Caravan, Reservation
from .validators import ReservationValidator
# from .payment_service import PaymentService # Placeholder
# from .notification_service import NotificationService # Placeholder

class ReservationService:
    def __init__(self, validator: ReservationValidator, payment_service=None, notification_service=None):
        self.validator = validator
        self.payment_service = payment_service
        self.notification_service = notification_service

    def create_reservation(self, user_id, caravan_id, start_date, end_date):
        user = User.objects.get(pk=user_id)
        caravan = Caravan.objects.get(pk=caravan_id)

        self.validator.validate(user, caravan, start_date, end_date)

        reservation = Reservation.objects.create(
            guest=user,
            caravan=caravan,
            start_date=start_date,
            end_date=end_date
        )

        # In a real application, you would call payment and notification services here.
        # self.payment_service.request_payment(reservation)
        # self.notification_service.notify(reservation.guest, "Reservation created")

        return reservation
