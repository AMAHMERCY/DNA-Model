

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from datetime import date

from .models import Appointment, AppointmentSlot
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    SlotAdminSerializer
)

# REAL ML IMPORT
from .services import predict_risk_and_intervention


# -------------------------------------------------------------------
#   BOOK APPOINTMENT  (with ML + booking rules)
# ------------------------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = request.user

    slot_id = data["slot_id"]

    slot = AppointmentSlot.objects.filter(id=slot_id, is_active=True).first()
    if not slot:
        return Response({"detail": "Selected time slot is invalid or inactive."}, status=400)

    appointment = Appointment.objects.create(
        patient=user,
        appointment_date=data["appointment_date"],
        slot_id=slot_id,
        reason=data["reason"],
        symptoms=data["symptoms"],
        other_symptoms=data.get("other_symptoms", ""),
    )

    # 🔹 ML: risk + intervention
    risk, intervention = predict_risk_and_intervention(user, appointment)
    appointment.risk_level = risk
    appointment.recommended_intervention = intervention
    appointment.save()

    return Response(
        {
            "message": "Appointment booked successfully",
            "appointment": AppointmentDetailSerializer(appointment).data,
        },
        status=201,
    )


# def book_appointment(request):
#     serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})

#     if not serializer.is_valid():
#         return Response(serializer.errors, status=400)

#     data = serializer.validated_data
#     user = request.user
#     selected_date = data["appointment_date"]
#     slot_id = data["slot_id"]

#     # RULE 1: No booking if user already has upcoming appointment
#     existing = Appointment.objects.filter(
#         patient=user,
#         appointment_date__gte=date.today()
#     )

#     if existing.exists():
#         return Response(
#             {"detail": "You already have an upcoming appointment. Cancel it first."},
#             status=400
#         )

#     # RULE 2: Slot must exist & be active
#     slot = AppointmentSlot.objects.filter(id=slot_id, is_active=True).first()
#     if not slot:
#         return Response({"detail": "Selected time slot is invalid or inactive."}, status=400)

#     # CREATE appointment
#     appointment = Appointment.objects.create(
#         patient=user,
#         appointment_date=selected_date,
#         slot_id=slot_id,
#         reason=data["reason"],
#         symptoms=data["symptoms"],
#         other_symptoms=data.get("other_symptoms", "")
#     )

#     # ---------------------------
#     # REAL ML RISK PREDICTION
#     # ---------------------------
#     risk, intervention = predict_risk_and_intervention(user, appointment)

#     appointment.risk_level = risk
#     appointment.recommended_intervention = intervention
#     appointment.save()

#     return Response(
#         {
#             "message": "Appointment booked successfully",
#             "appointment": AppointmentDetailSerializer(appointment).data,
#         },
#         status=201
#     )


# -------------------------------------------------------------------
#   USER — VIEW MY APPOINTMENTS
# -------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_appointments(request):
    user = request.user
    appointments = Appointment.objects.filter(patient=user)
    serializer = AppointmentDetailSerializer(appointments, many=True)
    return Response(serializer.data, status=200)


# -------------------------------------------------------------------
#   USER — CANCEL APPOINTMENT
# -------------------------------------------------------------------

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    user = request.user

    try:
        appointment = Appointment.objects.get(pk=pk, patient=user)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found"}, status=404)

    appointment.delete()
    return Response({"message": "Appointment cancelled"}, status=200)


# -------------------------------------------------------------------
#   ADMIN — VIEW ALL APPOINTMENTS
# -------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_get_all_appointments(request):
    user = request.user

    if user.role != "admin":
        return Response({"detail": "Not authorized"}, status=403)

    appointments = Appointment.objects.all().order_by("-appointment_date", "-created_at")
    serializer = AppointmentDetailSerializer(appointments, many=True)

    return Response(serializer.data, status=200)


# -------------------------------------------------------------------
#   SLOT MANAGEMENT FOR ADMIN
# -------------------------------------------------------------------

def is_admin(user):
    return hasattr(user, "role") and user.role == "admin"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_list_slots(request):
    if not is_admin(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    slots = AppointmentSlot.objects.all().order_by("start_time")
    return Response(SlotAdminSerializer(slots, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_create_slot(request):
    if not is_admin(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    serializer = SlotAdminSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def admin_update_slot(request, pk):
    if not is_admin(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    try:
        slot = AppointmentSlot.objects.get(pk=pk)
    except AppointmentSlot.DoesNotExist:
        return Response({"detail": "Slot not found"}, status=404)

    serializer = SlotAdminSerializer(slot, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def admin_toggle_slot(request, pk):
    if not is_admin(request.user):
        return Response({"detail": "Not authorized"}, status=403)

    try:
        slot = AppointmentSlot.objects.get(pk=pk)
    except AppointmentSlot.DoesNotExist:
        return Response({"detail": "Slot not found"}, status=404)

    slot.is_active = not slot.is_active
    slot.save()

    return Response({"message": "Updated", "is_active": slot.is_active})


# -------------------------------------------------------------------
#   GET ACTIVE SLOTS (PATIENT BOOKING FORM)
# -------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_active_slots(request):
    slots = AppointmentSlot.objects.filter(is_active=True).order_by("start_time")
    data = [
        {
            "id": slot.id,
            "start_time": slot.start_time.strftime("%H:%M"),
            "end_time": slot.end_time.strftime("%H:%M"),
        }
        for slot in slots
    ]
    return Response(data, status=200)
