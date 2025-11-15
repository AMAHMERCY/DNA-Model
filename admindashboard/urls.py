
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='admindashboard'),
    path('viewAppointments/', views.view_appointments, name='viewAppointments'),
    path('patientDetails/', views.view_patientDetails, name='patientDetails'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('booking/', views.booking_view, name='booking'),

]


