from django.urls import path
from .views import caravan_list_view, caravan_detail_view, signup_view, LoginView, LogoutView

urlpatterns = [
    path('', caravan_list_view, name='caravan-list'),
    path('caravan/<int:caravan_id>/', caravan_detail_view, name='caravan-detail'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
