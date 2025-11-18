from django.shortcuts import render

def home(request):
    return render(request, 'userdashboard/index.html')

def my_appointments(request):
    return render(request, 'userdashboard/myAppointments.html')

def view_userProfile(request):
    return render(request, 'userdashboard/user_profile.html')

def booking_view(request):
    return render(request, 'userdashboard/booking.html')



