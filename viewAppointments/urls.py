from django.urls import path
from . import views

urlpatterns = [
    path('viewAppointments/', views.view_appointments, name='viewAppointments'),
]