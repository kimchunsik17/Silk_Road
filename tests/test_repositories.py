import pytest
from datetime import date
from core.models import User, Caravan, Reservation
from core.repositories.caravan_repository import CaravanRepository
from core.repositories.reservation_repository import ReservationRepository as ReservationRepo

@pytest.mark.django_db
def test_caravan_repository_get_by_id():
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    repo = CaravanRepository()
    found_caravan = repo.get_by_id(caravan.id)
    assert found_caravan == caravan

@pytest.mark.django_db
def test_caravan_repository_find_available():
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan1 = Caravan.objects.create(host=host, name='Caravan 1', capacity=4)
    caravan2 = Caravan.objects.create(host=host, name='Caravan 2', capacity=2)
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    Reservation.objects.create(guest=guest, caravan=caravan1, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
    
    repo = CaravanRepository()
    available_caravans = repo.find_available(date(2025, 1, 1), date(2025, 1, 5), 2)
    assert caravan2 in available_caravans
    assert caravan1 not in available_caravans

@pytest.mark.django_db
def test_reservation_repository_check_conflict():
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    Reservation.objects.create(guest=guest, caravan=caravan, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))

    repo = ReservationRepo()
    assert repo.check_conflict(caravan.id, date(2025, 1, 2), date(2025, 1, 4)) == True
    assert repo.check_conflict(caravan.id, date(2025, 1, 6), date(2025, 1, 10)) == False
