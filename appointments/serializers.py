
from rest_framework import serializers
from .models import Appointment, AppointmentSlot

class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "start_time", "end_time", "is_active"]


# class AppointmentCreateSerializer(serializers.Serializer):
#     """
#     Used for incoming request body.
#     Patient is taken from request.user, not from the body.
#     """
#     appointment_date = serializers.DateField()
#     slot_id = serializers.IntegerField()
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

#     # def validate_slot_id(self, value):
#     #     from .models import AppointmentSlot
#     #     try:
#     #         slot = AppointmentSlot.objects.get(id=value, is_active=True)
#     #     except AppointmentSlot.DoesNotExist:
#     #         raise serializers.ValidationError("Invalid or inactive slot.")
#     #     return value
#     def validate_slot_id(self, value):
#     # TEMPORARY: allow placeholder IDs until admin slot creation is implemented
#      return value


#     def validate(self, attrs):
#         """
#         Enforce one appointment per patient per day.
#         """
#         request = self.context.get("request")
#         user = getattr(request, "user", None)
#         if not user or not user.is_authenticated:
#             raise serializers.ValidationError("Authentication required.")

#         from .models import Appointment
#         appointment_date = attrs["appointment_date"]

#         if Appointment.objects.filter(patient=user, appointment_date=appointment_date).exists():
#             raise serializers.ValidationError(
#                 "You already have an appointment on this date."
#             )

#         return attrs

class AppointmentCreateSerializer(serializers.Serializer):
    appointment_date = serializers.DateField()
    slot_id = serializers.IntegerField(required=False)
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

    def validate(self, attrs):
        """
        Allow temporary slot_id, enforce one-per-day booking.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        from .models import Appointment

        # One appointment per day
        appointment_date = attrs["appointment_date"]
        if Appointment.objects.filter(patient=user, appointment_date=appointment_date).exists():
            raise serializers.ValidationError("You already have an appointment on this date.")

        # TEMPORARY slot ID handling
        attrs["slot_id"] = attrs.get("slot_id", 1)  # placeholder slot

        return attrs

class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    slot = AppointmentSlotSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_email",
            "appointment_date",
            "slot",
            "reason",
            "symptoms",
            "other_symptoms",
            "risk_level",
            "recommended_intervention",
            "created_at",
        ]
