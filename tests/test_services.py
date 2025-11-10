import pytest
from datetime import date
from unittest.mock import Mock
from core.models import User, Caravan
from core.services.reservation_service import ReservationService
from core.services.validators import ReservationValidator

@pytest.fixture
def reservation_service():
    validator = Mock(spec=ReservationValidator)
    return ReservationService(validator)

@pytest.mark.django_db
def test_reservation_service_create_reservation(reservation_service):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    reservation = reservation_service.create_reservation(guest.id, caravan.id, date(2025, 1, 1), date(2025, 1, 5))

    reservation_service.validator.validate.assert_called_once_with(guest, caravan, date(2025, 1, 1), date(2025, 1, 5))
    assert reservation.guest == guest
    assert reservation.caravan == caravan
