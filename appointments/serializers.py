
from rest_framework import serializers
from .models import Appointment, AppointmentSlot
from datetime import date


class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "start_time", "end_time", "is_active"]


class SlotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "start_time", "end_time", "is_active"]


# class AppointmentCreateSerializer(serializers.Serializer):
#     appointment_date = serializers.DateField()
#     slot_id = serializers.IntegerField(required=False)
#     reason = serializers.CharField(max_length=255)
#     symptoms = serializers.ListField(
#         child=serializers.CharField(max_length=100),
#         allow_empty=True
#     )
#     other_symptoms = serializers.CharField(
#         max_length=255,
#         required=False,
#         allow_blank=True,
#         allow_null=True
#     )

#     # def validate(self, attrs):
#     #     """
#     #     Allow temporary slot_id + enforce one-per-day rule.
#     #     """
#     #     request = self.context.get("request")
#     #     user = getattr(request, "user", None)

#     #     if not user or not user.is_authenticated:
#     #         raise serializers.ValidationError("Authentication required.")

#     #     from .models import Appointment

#     #     # One appointment per day
#     #     appointment_date = attrs["appointment_date"]
#     #     if Appointment.objects.filter(patient=user, appointment_date=appointment_date).exists():
#     #         raise serializers.ValidationError("You already have an appointment on this date.")

#     #     # Temporary slot
#     #     attrs["slot_id"] = attrs.get("slot_id", 1)

#     #     return attrs

class AppointmentCreateSerializer(serializers.Serializer):
    reason = serializers.CharField()
    appointment_date = serializers.DateField()
    slot_id = serializers.IntegerField()
    symptoms = serializers.ListField(child=serializers.CharField())
    other_symptoms = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context["request"].user
        appt_date = attrs["appointment_date"]
        slot_id = attrs["slot_id"]

        # User cannot book future appointment if another future appointment exists
        if Appointment.objects.filter(
            patient=user,
            appointment_date__gte=date.today()
        ).exists():
            raise serializers.ValidationError(
                {"detail": "You already have an active appointment. Cancel it first."}
            )

        # Ensure slot exists & active
        if not AppointmentSlot.objects.filter(id=slot_id, is_active=True).exists():
            raise serializers.ValidationError(
                {"slot_id": "Invalid or inactive appointment slot"}
            )

        return attrs

# class AppointmentDetailSerializer(serializers.ModelSerializer):
#     patient_email = serializers.EmailField(source="patient.email", read_only=True)
#     slot = AppointmentSlotSerializer(read_only=True)

#     class Meta:
#         model = Appointment
#         fields = [
#             "id",
#             "patient_email",
#             "appointment_date",
#             "slot",
#             "reason",
#             "symptoms",
#             "other_symptoms",
#             "risk_level",
#             "recommended_intervention",
#             "created_at",
#         ]

class AppointmentDetailSerializer(serializers.ModelSerializer):
    slot_time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
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
            return "No slot"


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
            raise serializers.ValidationError("Invalid or inactive slot.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        appointment_date = attrs["appointment_date"]

        # Rule: **User cannot book more than one future appointment**
        if Appointment.objects.filter(patient=user, appointment_date__gte=date.today()).exists():
            raise serializers.ValidationError(
                "You already have a booked appointment. Please cancel it or wait until the date has passed."
            )

        return attrs