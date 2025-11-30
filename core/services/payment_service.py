import requests
from django.conf import settings
from django.utils import timezone
from ..models import Payment, Reservation
from ..exceptions import PaymentFailedError

class PaymentService:
    def request_payment(self, user, amount):
        # This method is now a placeholder for other payment methods
        print(f"Requesting payment of {amount} for user {user.username}")
        return True 

    def confirm_payment(self, payment_key, order_id, amount):
        url = "https://api.tosspayments.com/v1/payments/confirm"
        headers = {
            "Authorization": f"Basic {settings.TOSS_PAYMENTS_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount,
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == "DONE":
            # Assuming order_id is in the format 'order__{reservation_id}'
            try:
                reservation_id = int(order_id.split('__')[1])
                reservation = Reservation.objects.get(id=reservation_id)
            except (IndexError, ValueError, Reservation.DoesNotExist):
                raise PaymentFailedError("Invalid order ID.")

            Payment.objects.create(
                reservation=reservation,
                amount=amount,
                status=Payment.PaymentStatus.PAID,
                paid_at=timezone.now(),
                payment_key=payment_key
            )
        else:
            raise PaymentFailedError(response_data.get("message", "Payment confirmation failed."))
