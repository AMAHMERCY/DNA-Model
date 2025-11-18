
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='userdashboard'),
    path('myAppointments/', views.my_appointments, name='myAppointments'),
    path('user_profile/', views.view_userProfile, name='user_profile'),
    path('booking/', views.booking_view, name='booking'),

]


