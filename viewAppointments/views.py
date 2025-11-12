
from django.shortcuts import render

# Create your views here.

def view_appointments(request):
    return render(request, 'viewAppointments/viewAppointments.html')

