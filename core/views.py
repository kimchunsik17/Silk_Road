from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
import json
from .models import Caravan
from .services.reservation_service import ReservationService
from .repositories.reservation_repository import ReservationRepository
from .services.validators import ReservationValidator
from .exceptions import ReservationConflictError, InsufficientPermissionsError
from .forms import ReservationForm, CustomUserCreationForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def caravan_list_view(request):
    caravans = Caravan.objects.all()
    return render(request, 'caravan_list.html', {'caravans': caravans})

@login_required
def caravan_detail_view(request, caravan_id):
    caravan = get_object_or_404(Caravan, pk=caravan_id)
    return render(request, 'caravan_detail.html', {'caravan': caravan})

@login_required
@require_POST
def create_reservation_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Security: Ignore user_id from payload, use the logged-in user
    data['user_id'] = request.user.id
    
    form = ReservationForm(data)

    if not form.is_valid():
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    cleaned_data = form.cleaned_data
    user_id = cleaned_data['user_id']
    caravan_id = cleaned_data['caravan_id']
    start_date = cleaned_data['start_date']
    end_date = cleaned_data['end_date']

    try:
        # Manual dependency injection for now
        reservation_repo = ReservationRepository()
        validator = ReservationValidator(reservation_repo)
        service = ReservationService(validator)

        reservation = service.create_reservation(user_id, caravan_id, start_date, end_date)

        return JsonResponse({'status': 'success', 'reservation_id': reservation.id}, status=201)
    except (ReservationConflictError, InsufficientPermissionsError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        # It's better to log the exception here in a real app
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)
