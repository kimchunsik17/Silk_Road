import pytest
from datetime import date
from core.models import User, Caravan, Reservation, Payment, Review

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(username='testuser', password='password', user_type=User.UserType.GUEST)
    assert user.username == 'testuser'
    assert user.user_type == User.UserType.GUEST

@pytest.mark.django_db
def test_caravan_creation():
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    assert caravan.name == 'Test Caravan'
    assert caravan.host == host

@pytest.mark.django_db
def test_reservation_creation():
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    reservation = Reservation.objects.create(guest=guest, caravan=caravan, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
    assert reservation.guest == guest
    assert reservation.caravan == caravan

@pytest.mark.django_db
def test_payment_creation():
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    reservation = Reservation.objects.create(guest=guest, caravan=caravan, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
    payment = Payment.objects.create(reservation=reservation, amount=100.00, status=Payment.PaymentStatus.PAID)
    assert payment.reservation == reservation
    assert payment.amount == 100.00

@pytest.mark.django_db
def test_review_creation():
    guest = User.objects.create_user(username='guest', password='password', user_type=User.UserType.GUEST)
    host = User.objects.create_user(username='host', password='password', user_type=User.UserType.HOST)
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    reservation = Reservation.objects.create(guest=guest, caravan=caravan, start_date=date(2025, 1, 1), end_date=date(2025, 1, 5))
    review = Review.objects.create(reservation=reservation, reviewer=guest, target_user=host, rating=5, comment='Great caravan!')
    assert review.rating == 5
    assert review.reviewer == guest
