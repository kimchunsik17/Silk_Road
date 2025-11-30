from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
import json
from datetime import timedelta, datetime
from .models import Caravan, Reservation, User, Chat, PaymentMethod
from django.db.models import Q
from .services.reservation_service import ReservationService
from .repositories.reservation_repository import ReservationRepository
from .services.validators import ReservationValidator
from .services.payment_service import PaymentService
from .services.notification_service import NotificationService
from .services.pricing_strategy import StandardPricingStrategy
from .exceptions import ReservationConflictError, InsufficientPermissionsError, PaymentFailedError
from .forms import (
    ReservationForm, 
    CustomUserCreationForm, 
    CaravanForm, 
    CaravanImageFormSet, 
    CaravanImageForm, 
    BlockedPeriodFormSet,
    UserProfileForm,
    PaymentMethodForm
)
from django.conf import settings
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('caravan-list')

@login_required
def create_caravan_view(request):
    if request.user.user_type != 'HOST':
        return HttpResponseForbidden("You are not authorized to host a caravan.")

    if request.method == 'POST':
        form = CaravanForm(request.POST)
        formset = CaravanImageFormSet(request.POST, request.FILES, queryset=Caravan.objects.none())

        if form.is_valid() and formset.is_valid():
            caravan = form.save(commit=False)
            caravan.host = request.user
            caravan.save()
            
            for form_in_formset in formset:
                if form_in_formset.cleaned_data:
                    if not form_in_formset.cleaned_data.get('DELETE', False):
                        image = form_in_formset.save(commit=False)
                        image.caravan = caravan
                        image.save()
            
            return redirect('caravan-detail', caravan_id=caravan.id)
    else:
        form = CaravanForm()
        formset = CaravanImageFormSet(queryset=Caravan.objects.none())
        
    return render(request, 'caravan_form.html', {'form': form, 'image_formset': formset})

@login_required
def update_caravan_view(request, caravan_id):
    caravan = get_object_or_404(Caravan, pk=caravan_id)
    if request.user != caravan.host:
        return HttpResponseForbidden("You are not the host of this caravan.")

    if request.method == 'POST':
        form = CaravanForm(request.POST, instance=caravan)
        image_formset = CaravanImageFormSet(request.POST, request.FILES, queryset=caravan.images.all())
        blocked_period_formset = BlockedPeriodFormSet(request.POST, queryset=caravan.blocked_periods.all())
        
        if form.is_valid() and image_formset.is_valid() and blocked_period_formset.is_valid():
            form.save()
            
            # Save image formset
            image_formset.save()

            # Save blocked period formset, assigning caravan to new instances
            instances = blocked_period_formset.save(commit=False)
            for instance in instances:
                instance.caravan = caravan
                instance.save()
            # Handle deletions
            for form in blocked_period_formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            return redirect('caravan-detail', caravan_id=caravan.id)
    else:
        form = CaravanForm(instance=caravan)
        image_formset = CaravanImageFormSet(queryset=caravan.images.all())
        blocked_period_formset = BlockedPeriodFormSet(queryset=caravan.blocked_periods.all())

    reservations = Reservation.objects.filter(caravan=caravan)
    reserved_dates = []
    for reservation in reservations:
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            reserved_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
            
    context = {
        'form': form,
        'caravan': caravan,
        'image_formset': image_formset,
        'blocked_period_formset': blocked_period_formset,
        'reserved_dates': json.dumps(reserved_dates)
    }
    
    return render(request, 'caravan_form.html', context)

def caravan_list_view(request):
    query = request.GET.get('q')
    if query:
        caravans = Caravan.objects.filter(name__icontains=query).order_by('-created_at')
    else:
        caravans = Caravan.objects.all().order_by('-created_at')
    return render(request, 'caravan_list.html', {'caravans': caravans})

def caravan_detail_view(request, caravan_id):
    caravan = get_object_or_404(Caravan, pk=caravan_id)
    reservations = caravan.reservations.all()
    blocked_periods = caravan.blocked_periods.all()
    caravan_images = caravan.images.all()
    
    unavailable_dates = []
    # Add dates from reservations
    for reservation in reservations:
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    # Add dates from blocked periods
    for period in blocked_periods:
        current_date = period.start_date
        while current_date <= period.end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
            
    return render(request, 'caravan_detail.html', {
        'caravan': caravan,
        'reserved_dates': json.dumps(list(set(unavailable_dates))), # Use set to remove duplicates
        'caravan_images': caravan_images,
    })

@login_required
def checkout_view(request, caravan_id):
    caravan = get_object_or_404(Caravan, pk=caravan_id)

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        # Basic validation
        if not start_date_str or not end_date_str:
            messages.error(request, "Please select a start and end date.")
            return redirect('checkout', caravan_id=caravan_id)

        try:
            # Convert string dates to date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Manual dependency injection
            reservation_repo = ReservationRepository()
            validator = ReservationValidator(reservation_repo)
            payment_service = PaymentService()
            notification_service = NotificationService()
            pricing_strategy = StandardPricingStrategy()
            service = ReservationService(validator, payment_service, notification_service, pricing_strategy)

            service.create_reservation(request.user.id, caravan.id, start_date, end_date)

            messages.success(request, "Your reservation has been successfully created!")
            return redirect('profile')

        except (ReservationConflictError, InsufficientPermissionsError, PaymentFailedError) as e:
            messages.error(request, str(e))
            return redirect('checkout', caravan_id=caravan_id)
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('checkout', caravan_id=caravan_id)
        except Exception as e:
            # Temporarily expose the actual error for debugging, escaping it for safety
            error_message = f"An unexpected error occurred: {escape(e)}"
            messages.error(request, error_message)
            return redirect('checkout', caravan_id=caravan_id)

    # GET request logic
    reservations = caravan.reservations.all()
    blocked_periods = caravan.blocked_periods.all()
    
    unavailable_dates = []
    for reservation in reservations:
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    for period in blocked_periods:
        current_date = period.start_date
        while current_date <= period.end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
            
    context = {
        'caravan': caravan,
    }
    
    return render(request, 'checkout.html', context)

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
        payment_service = PaymentService()
        notification_service = NotificationService()
        pricing_strategy = StandardPricingStrategy()
        service = ReservationService(validator, payment_service, notification_service, pricing_strategy)

        reservation = service.create_reservation(user_id, caravan_id, start_date, end_date)

        return JsonResponse({'status': 'success', 'reservation_id': reservation.id}, status=201)
    except (ReservationConflictError, InsufficientPermissionsError, PaymentFailedError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        # It's better to log the exception here in a real app
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)

@login_required
def chat_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if request.user == receiver:
        return redirect('caravan-list')

    room_name = '_'.join(sorted([str(request.user.id), str(receiver.id)]))
    
    chat_history = Chat.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(sender=receiver) & Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'chat.html', {
        'receiver': receiver,
        'room_name': room_name,
        'chat_history': chat_history
    })

@login_required
def caravan_image_upload_view(request, caravan_id):
    caravan = get_object_or_404(Caravan, pk=caravan_id)

    if request.user != caravan.host:
        return HttpResponseForbidden("You are not the host of this caravan.")

    if request.method == 'POST':
        form = CaravanImageForm(request.POST, request.FILES)
        if form.is_valid():
            caravan_image = form.save(commit=False)
            caravan_image.caravan = caravan
            caravan_image.save()
            return redirect('caravan-detail', caravan_id=caravan.id)
    else:
        form = CaravanImageForm()
    
    return render(request, 'caravan_image_upload.html', {'caravan': caravan, 'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('profile')
        elif 'add_payment_method' in request.POST:
            payment_form = PaymentMethodForm(request.POST)
            if payment_form.is_valid():
                payment_method = payment_form.save(commit=False)
                payment_method.user = request.user
                payment_method.save()
                messages.success(request, 'Payment method added successfully.')
                return redirect('profile')

    profile_form = UserProfileForm(instance=request.user)
    payment_form = PaymentMethodForm()
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    reservations = Reservation.objects.filter(guest=request.user)

    context = {
        'profile_form': profile_form,
        'payment_form': payment_form,
        'payment_methods': payment_methods,
        'reservations': reservations
    }
    return render(request, 'profile.html', context)