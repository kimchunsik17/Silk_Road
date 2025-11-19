import pytest
from datetime import date
from unittest.mock import Mock
from core.models import User, Caravan, Reservation
from core.services.reservation_service import ReservationService
from core.services.validators import ReservationValidator
from core.services.payment_service import PaymentService
from core.services.notification_service import NotificationService
from core.services.pricing_strategy import StandardPricingStrategy
from core.exceptions import PaymentFailedError

@pytest.fixture
def mock_validator():
    return Mock(spec=ReservationValidator)

@pytest.fixture
def mock_payment_service():
    return Mock(spec=PaymentService)

@pytest.fixture
def mock_notification_service():
    return Mock(spec=NotificationService)

@pytest.fixture
def mock_pricing_strategy():
    return Mock(spec=StandardPricingStrategy)

@pytest.fixture
def reservation_service(mock_validator, mock_payment_service, mock_notification_service, mock_pricing_strategy):
    return ReservationService(mock_validator, mock_payment_service, mock_notification_service, mock_pricing_strategy)

@pytest.mark.django_db
def test_reservation_service_create_reservation_success(reservation_service, mock_validator, mock_payment_service, mock_notification_service, mock_pricing_strategy):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    mock_pricing_strategy.calculate_price.return_value = 500.00
    mock_payment_service.request_payment.return_value = True

    reservation = reservation_service.create_reservation(guest.id, caravan.id, date(2025, 1, 1), date(2025, 1, 5))

    mock_validator.validate.assert_called_once_with(guest, caravan, date(2025, 1, 1), date(2025, 1, 5))
    mock_pricing_strategy.calculate_price.assert_called_once_with(caravan, date(2025, 1, 1), date(2025, 1, 5))
    mock_payment_service.request_payment.assert_called_once_with(guest, 500.00)
    mock_notification_service.notify.assert_called_once_with(guest, f"Reservation for {caravan.name} created and paid.")
    
    assert reservation.guest == guest
    assert reservation.caravan == caravan
    assert reservation.start_date == date(2025, 1, 1)
    assert reservation.end_date == date(2025, 1, 5)

@pytest.mark.django_db
def test_reservation_service_create_reservation_payment_failure(reservation_service, mock_validator, mock_payment_service, mock_notification_service, mock_pricing_strategy):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    mock_pricing_strategy.calculate_price.return_value = 500.00
    mock_payment_service.request_payment.return_value = False

    with pytest.raises(PaymentFailedError):
        reservation_service.create_reservation(guest.id, caravan.id, date(2025, 1, 1), date(2025, 1, 5))

    mock_validator.validate.assert_called_once_with(guest, caravan, date(2025, 1, 1), date(2025, 1, 5))
    mock_pricing_strategy.calculate_price.assert_called_once_with(caravan, date(2025, 1, 1), date(2025, 1, 5))
    mock_payment_service.request_payment.assert_called_once_with(guest, 500.00)
    mock_notification_service.notify.assert_not_called()
