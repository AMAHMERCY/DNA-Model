
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='admindashboard'),
    path('viewAppointments/', views.view_appointments, name='viewAppointments'),
    path('patientDetails/', views.view_patientDetails, name='patientDetails'),
    path('booking/', views.booking_view, name='booking'),

]


