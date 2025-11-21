from django.urls import path
from .views import (
    caravan_list_view, 
    caravan_detail_view, 
    signup_view, 
    LoginView, 
    create_reservation_view, 
    profile_view, 
    chat_view, 
    caravan_image_upload_view, 
    custom_logout_view,
    create_caravan_view,
    update_caravan_view,
    checkout_view
)

urlpatterns = [
    path('', caravan_list_view, name='caravan-list'),
    path('caravan/new/', create_caravan_view, name='create-caravan'),
    path('caravan/<int:caravan_id>/', caravan_detail_view, name='caravan-detail'),
    path('caravan/<int:caravan_id>/edit/', update_caravan_view, name='update-caravan'),
    path('caravan/<int:caravan_id>/checkout/', checkout_view, name='checkout'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('api/reservations/', create_reservation_view, name='create-reservation'),
    path('profile/', profile_view, name='profile'),
    path('chat/<int:user_id>/', chat_view, name='chat'),
    path('caravan/<int:caravan_id>/upload-image/', caravan_image_upload_view, name='caravan-image-upload'),
]
