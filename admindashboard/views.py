from django.shortcuts import render

def home(request):
    return render(request, 'admindashboard/index.html')

def view_appointments(request):
    return render(request, 'admindashboard/viewAppointments.html')

def view_patientDetails(request):
    return render(request, 'admindashboard/patientDetails.html')


def login_view(request):
    return render(request, 'admindashboard/login.html')

def register_view(request):
    return render(request, 'admindashboard/register.html')

def booking_view(request):
    return render(request, 'admindashboard/booking.html')


