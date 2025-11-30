from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from core.models import User, Caravan, Reservation, Payment
from datetime import date

class TossPaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.host = User.objects.create_user(username='host', password='password', user_type='HOST')
        self.guest = User.objects.create_user(username='guest', password='password', user_type='GUEST')
        self.caravan = Caravan.objects.create(
            host=self.host,
            name='Test Caravan',
            capacity=4,
            location='Test Location',
        )
        self.reservation = Reservation.objects.create(
            guest=self.guest,
            caravan=self.caravan,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
            status='PENDING'
        )

    @patch('requests.post')
    def test_toss_success_view(self, mock_post):
        # Mock the Toss Payments API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "DONE",
            "paymentKey": "test_payment_key",
            "orderId": f"order__{self.reservation.id}",
            "totalAmount": 1000,
        }
        mock_post.return_value = mock_response

        self.client.login(username='guest', password='password')
        response = self.client.get(reverse('toss_success'), {
            'paymentKey': 'test_payment_key',
            'orderId': f'order__{self.reservation.id}',
            'amount': '1000'
        })

        # Check that the user is redirected to the profile page
        self.assertRedirects(response, reverse('profile'))

        # Check that a Payment object was created
        payment = Payment.objects.get(reservation=self.reservation)
        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.payment_key, 'test_payment_key')
        self.assertEqual(payment.amount, 1000)

    def test_toss_fail_view(self):
        self.client.login(username='guest', password='password')
        response = self.client.get(reverse('toss_fail'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'toss_fail.html')

    @patch('requests.post')
    def test_confirm_payment_service_success(self, mock_post):
        from core.services.payment_service import PaymentService

        # Mock the Toss Payments API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "DONE",
            "paymentKey": "test_payment_key",
            "orderId": f"order__{self.reservation.id}",
            "totalAmount": 1000,
        }
        mock_post.return_value = mock_response

        payment_service = PaymentService()
        payment_service.confirm_payment('test_payment_key', f'order__{self.reservation.id}', 1000)

        # Check that a Payment object was created
        payment = Payment.objects.get(reservation=self.reservation)
        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.payment_key, 'test_payment_key')
        self.assertEqual(payment.amount, 1000)

    @patch('requests.post')
    def test_confirm_payment_service_fail(self, mock_post):
        from core.services.payment_service import PaymentService
        from core.exceptions import PaymentFailedError

        # Mock the Toss Payments API response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "status": "FAILED",
            "message": "Invalid API key",
        }
        mock_post.return_value = mock_response

        payment_service = PaymentService()

        with self.assertRaises(PaymentFailedError):
            payment_service.confirm_payment('test_payment_key', f'order__{self.reservation.id}', 1000)
