# appointments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Appointment, AppointmentSlot
from .serializers import AppointmentCreateSerializer, AppointmentDetailSerializer
from .services import fake_predict_risk_and_intervention


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    serializer = AppointmentCreateSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    user = request.user

    # TEMPORARY slot handling (since real admin creation isn't ready)
    slot_id = data["slot_id"]

    AppointmentSlot.objects.get_or_create(
        id=slot_id,
        defaults={
            "start_time": "09:00:00",
            "end_time": "09:30:00",
            "is_active": True,
        }
    )

    # CREATE appointment — USE slot_id (not slot)
    appointment = Appointment.objects.create(
        patient=user,
        appointment_date=data["appointment_date"],
        slot_id=slot_id,   # IMPORTANT CHANGE
        reason=data["reason"],
        symptoms=data["symptoms"],
        other_symptoms=data.get("other_symptoms", ""),
        risk_level="pending",
        recommended_intervention="pending",
    )

    # run placeholder ML model
    risk, intervention = fake_predict_risk_and_intervention(user, appointment)
    appointment.risk_level = risk
    appointment.recommended_intervention = intervention
    appointment.save()

    return Response(
        {
            "message": "Appointment booked successfully",
            "appointment": AppointmentDetailSerializer(appointment).data,
        },
        status=status.HTTP_201_CREATED,
    )
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_appointments(request):
    user = request.user
    appointments = Appointment.objects.filter(patient=user)
    serializer = AppointmentDetailSerializer(appointments, many=True)
    return Response(serializer.data, status=200)
