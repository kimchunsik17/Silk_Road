from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .services.reservation_service import ReservationService
from .repositories.reservation_repository import ReservationRepository
from .services.validators import ReservationValidator
from .exceptions import ReservationConflictError, InsufficientPermissionsError

@csrf_exempt
@require_POST
def create_reservation_view(request):
    try:
        data = json.loads(request.body)
        user_id = data['user_id']
        caravan_id = data['caravan_id']
        start_date = data['start_date']
        end_date = data['end_date']

        reservation_repo = ReservationRepository()
        validator = ReservationValidator(reservation_repo)
        service = ReservationService(validator)

        reservation = service.create_reservation(user_id, caravan_id, start_date, end_date)

        return JsonResponse({'status': 'success', 'reservation_id': reservation.id}, status=201)
    except (ReservationConflictError, InsufficientPermissionsError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
