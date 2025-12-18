from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from appointments.models import Appointment
from appointments.communications import (
    send_sms,
    send_confirm_sms,
    make_automated_call,
)


class Command(BaseCommand):
    help = "Send automated reminders 24 hours before appointment"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        tomorrow_start = (now + timedelta(hours=23)).replace(minute=0, second=0)
        tomorrow_end = (now + timedelta(hours=25)).replace(minute=59, second=59)

        appointments = Appointment.objects.filter(
            appointment_date=tomorrow_start.date()
        )

        if not appointments.exists():
            self.stdout.write("ℹ️ No appointments due in 24 hours")
            return

        for appt in appointments:
            user = appt.patient
            phone = user.phone

            if not phone:
                self.stdout.write(
                    f"⚠️ No phone number for user {user.email}, skipping"
                )
                continue

            # -------------------------
            # LOW RISK → SMS
            # -------------------------
            if appt.risk_level == "low":
                send_sms(
                    phone,
                    f"Reminder: You have an appointment tomorrow ({appt.appointment_date})."
                )

            # -------------------------
            # MEDIUM RISK → CONFIRM SMS
            # -------------------------
            elif appt.risk_level == "medium":
                send_confirm_sms(
                    phone,
                    f"Please confirm your appointment tomorrow ({appt.appointment_date}). Reply YES or NO."
                )

            # -------------------------
            # HIGH RISK → CALL → fallback SMS
            # -------------------------
            elif appt.risk_level == "high":
                answered = make_automated_call(
                    phone,
                    "This is a reminder for your NHS appointment tomorrow."
                )

                if not answered:
                    send_sms(
                        phone,
                        "We tried calling you. Please confirm your appointment tomorrow."
                    )

            self.stdout.write(
                f"✅ Reminder processed for {user.email} ({appt.risk_level})"
            )

        self.stdout.write("🎯 Reminder job completed")
