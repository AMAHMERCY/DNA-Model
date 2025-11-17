from django.db import models
from django.conf import settings

class AppointmentSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Appointment(models.Model):
    RISK_LEVEL_CHOICES = [
        ("pending", "Pending"),
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    INTERVENTION_CHOICES = [
        ("pending", "Pending"),
        ("sms", "SMS reminder"),
        ("sms_confirm", "SMS requiring confirmation"),
        ("sms_call", "SMS + call"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()

    # placeholder slot ID
    slot_id = models.IntegerField(default=1)

    reason = models.CharField(max_length=255)
    symptoms = models.JSONField(default=list)
    other_symptoms = models.CharField(max_length=255, blank=True, null=True)

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default="pending"
    )
    recommended_intervention = models.CharField(
        max_length=50,
        choices=INTERVENTION_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "appointment_date")
        ordering = ["-appointment_date", "-created_at"]

    def __str__(self):
        return f"{self.patient.email} - {self.appointment_date} (Slot ID: {self.slot_id})"
