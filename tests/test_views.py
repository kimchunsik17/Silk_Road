import json
import pytest
from datetime import date
from django.urls import reverse
from core.models import User, Caravan, Reservation

@pytest.mark.django_db
def test_create_reservation_success(client):
    host = User.objects.create_user(username='host', password='password', user_type='HOST')
    guest = User.objects.create_user(username='guest', password='password', user_type='GUEST')
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    url = reverse('create-reservation')
    data = {
        'user_id': guest.id,
        'caravan_id': caravan.id,
        'start_date': '2025-01-10',
        'end_date': '2025-01-15',
    }
    
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    
    assert response.status_code == 201
    assert response.json()['status'] == 'success'
    assert 'reservation_id' in response.json()
    assert Reservation.objects.filter(id=response.json()['reservation_id']).exists()

@pytest.mark.django_db
def test_create_reservation_invalid_input(client):
    url = reverse('create-reservation')
    data = {
        'user_id': 1,
        # caravan_id is missing
        'start_date': '2025-01-10',
        'end_date': '2025-01-15',
    }
    
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    
    assert response.status_code == 400
    assert response.json()['status'] == 'error'
    assert 'caravan_id' in response.json()['errors']

@pytest.mark.django_db
def test_create_reservation_conflict(client):
    host = User.objects.create_user(username='host', password='password', user_type='HOST')
    guest = User.objects.create_user(username='guest', password='password', user_type='GUEST')
    other_guest = User.objects.create_user(username='other_guest', password='password', user_type='GUEST')
    caravan = Caravan.objects.create(host=host, name='Test Caravan', capacity=4)
    
    # Existing reservation
    Reservation.objects.create(
        guest=other_guest,
        caravan=caravan,
        start_date=date(2025, 1, 12),
        end_date=date(2025, 1, 18)
    )
    
    url = reverse('create-reservation')
    data = {
        'user_id': guest.id,
        'caravan_id': caravan.id,
        'start_date': '2025-01-10',
        'end_date': '2025-01-15',
    }
    
    response = client.post(url, data=json.dumps(data), content_type='application/json')
    
    assert response.status_code == 400
    assert response.json()['status'] == 'error'
    assert 'Caravan is not available' in response.json()['message']

@pytest.mark.django_db
def test_create_reservation_bad_json(client):
    url = reverse('create-reservation')
    
    response = client.post(url, data='{bad json', content_type='application/json')
    
    assert response.status_code == 400
    assert response.json()['status'] == 'error'
    assert response.json()['message'] == 'Invalid JSON'
