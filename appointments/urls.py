
from django.urls import path
from .views import book_appointment, get_my_appointments

urlpatterns = [
    path("book/", book_appointment, name="book_appointment"),
    path("my-appointments/",get_my_appointments, name="api_my_appointments"),

]
