
# from django.urls import path
# from .views import book_appointment, get_my_appointments, admin_get_all_appointments, list_slots, create_slot, update_slot, toggle_slot

# urlpatterns = [
#     path("book/", book_appointment, name="book_appointment"),
#     path("my-appointments/",get_my_appointments, name="api_my_appointments"),
#     path("admin/all/", admin_get_all_appointments, name="api_admin_all_appointments"),
#     path("admin/slots/", list_slots, name="list_slots"),
#     path("admin/slots/create/", create_slot, name="create_slot"),
#     path("admin/slots/<int:pk>/update/", update_slot, name="update_slot"),
#     path("admin/slots/<int:pk>/toggle/", toggle_slot, name="toggle_slot"),

# ]


from django.urls import path
from .views import (
    book_appointment,
    get_my_appointments,
    admin_get_all_appointments,
    admin_list_slots,
    admin_create_slot,
    admin_update_slot,
    admin_toggle_slot,
    get_active_slots,
    cancel_appointment,
)

urlpatterns = [
    path("booking/", book_appointment),
    path("my-appointments/", get_my_appointments, name="api_my_appointments"),
    path("admin/all/", admin_get_all_appointments, name="api_admin_appointments"),

    # slot management
    path("admin/slots/", admin_list_slots),
    path("admin/slots/create/", admin_create_slot),
    path("admin/slots/<int:pk>/update/", admin_update_slot),
    path("admin/slots/<int:pk>/toggle/", admin_toggle_slot),
    path("slots/", get_active_slots, name="get_slots"),
    path("cancel/<int:pk>/", cancel_appointment),


]
