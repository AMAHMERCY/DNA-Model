from django.urls import path
from .views import register_patient,login_user

urlpatterns = [
    path('register/', register_patient, name='register'),
    path("login/", login_user, name="login"),

]
