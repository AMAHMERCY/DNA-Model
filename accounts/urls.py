from django.urls import path
from .views import register_patient,login_user,get_user_profile, update_user_profile

urlpatterns = [
    path('register/', register_patient, name='api_register'),
    path("login/", login_user, name="api_login"),
    path("profile/", get_user_profile, name="user_profile"),
    path("profile/update/", update_user_profile, name="profile_update"),
    
]
