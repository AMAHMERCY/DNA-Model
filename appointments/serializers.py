# XGBOOST
from rest_framework import serializers
from .models import Appointment, AppointmentSlot
from datetime import date


# ------------------------------------------------------------
# SLOT SERIALIZERS
# ------------------------------------------------------------
class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "start_time", "end_time", "is_active"]


class SlotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "start_time", "end_time", "is_active"]


# ------------------------------------------------------------
# CREATE APPOINTMENT SERIALIZER
# ------------------------------------------------------------
class AppointmentCreateSerializer(serializers.Serializer):
    appointment_date = serializers.DateField()
    slot_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=255)
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True
    )
    other_symptoms = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True
    )

    def validate_slot_id(self, value):
        """Ensure slot exists and is active."""
        try:
            AppointmentSlot.objects.get(id=value, is_active=True)
        except AppointmentSlot.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive appointment slot.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        appointment_date = attrs["appointment_date"]

        # One future appointment rule
        if Appointment.objects.filter(
            patient=user,
            appointment_date__gte=date.today()
        ).exists():
            raise serializers.ValidationError(
                "You already have a booked appointment. Cancel it or wait until the date has passed."
            )

        return attrs


# ------------------------------------------------------------
# DETAIL SERIALIZER (ADMIN + USER)
# ------------------------------------------------------------

class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    patient_hospital_id = serializers.CharField(source="patient.hospital_id", read_only=True)
    slot_time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "patient_hospital_id",
            "patient_email",
            "appointment_date",
            "reason",
            "symptoms",
            "other_symptoms",
            "slot_id",
            "slot_time",
            "risk_level",
            "recommended_intervention",
            "created_at",
        ]

    def get_slot_time(self, obj):
        try:
            slot = AppointmentSlot.objects.get(id=obj.slot_id)
            return f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
        except AppointmentSlot.DoesNotExist:
            return "—"
