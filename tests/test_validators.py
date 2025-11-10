import pytest
from datetime import date
from core.models import User, Caravan, Reservation
from core.services.validators import ReservationValidator
from core.repositories.reservation_repository import ReservationRepository
from core.exceptions import ReservationConflictError, InsufficientPermissionsError

@pytest.fixture
def reservation_validator():
    return ReservationValidator(ReservationRepository())

@pytest.mark.django_db
def test_validator_success(reservation_validator):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    reservation_validator.validate(guest, caravan, date(2025, 1, 1), date(2025, 1, 5))
    # No exception should be raised

@pytest.mark.django_db
def test_validator_raises_conflict_error(reservation_validator):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    Reservation.objects.create(guest=guest, caravan=caravan, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))

    with pytest.raises(ReservationConflictError):
        reservation_validator.validate(guest, caravan, date(2025, 1, 2), date(2025, 1, 4))

@pytest.mark.django_db
def test_validator_raises_permission_error(reservation_validator):
    host_user = User.objects.create_user(username='host_user', password='password', user_type=User.UserType.HOST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)

    with pytest.raises(InsufficientPermissionsError):
        reservation_validator.validate(host_user, caravan, date(2025, 1, 1), date(2025, 1, 5))

@pytest.mark.django_db
def test_validator_raises_caravan_not_available_error(reservation_validator):
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4, status=Caravan.CaravanStatus.MAINTENANCE)

    with pytest.raises(ReservationConflictError):
        reservation_validator.validate(guest, caravan, date(2025, 1, 1), date(2025, 1, 5))
