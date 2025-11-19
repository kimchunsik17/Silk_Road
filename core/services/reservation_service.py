from core.models import User, Caravan, Reservation
from core.exceptions import PaymentFailedError
from .validators import ReservationValidator
from .payment_service import PaymentService
from .notification_service import NotificationService
from .pricing_strategy import StandardPricingStrategy

class ReservationService:
    def __init__(self, validator: ReservationValidator, payment_service: PaymentService, notification_service: NotificationService, pricing_strategy: StandardPricingStrategy):
        self.validator = validator
        self.payment_service = payment_service
        self.notification_service = notification_service
        self.pricing_strategy = pricing_strategy

    def _create_reservation_object(self, guest, caravan, start_date, end_date):
        return Reservation.objects.create(
            guest=guest,
            caravan=caravan,
            start_date=start_date,
            end_date=end_date
        )

    def create_reservation(self, user_id, caravan_id, start_date, end_date):
        user = User.objects.get(pk=user_id)
        caravan = Caravan.objects.get(pk=caravan_id)

        self.validator.validate(user, caravan, start_date, end_date)

        # Calculate price
        total_amount = self.pricing_strategy.calculate_price(caravan, start_date, end_date)

        # Request payment
        if not self.payment_service.request_payment(user, total_amount):
            raise PaymentFailedError("Payment failed for the reservation.")

        # Create Reservation object using factory pattern
        reservation = self._create_reservation_object(user, caravan, start_date, end_date)

        # Notify
        self.notification_service.notify(reservation.guest, f"Reservation for {caravan.name} created and paid.")

        return reservation
