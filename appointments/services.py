import joblib
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from django.utils import timezone
from accounts.imd_lookup import lookup_imd
from .models import Appointment, AppointmentSlot
from twilio.rest import Client
import os
from django.conf import settings

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_PHONE_NUMBER")
print("DEBUG TWILIO_SID:", TWILIO_SID)
print("DEBUG TWILIO_TOKEN:", bool(TWILIO_TOKEN))
print("DEBUG TWILIO_FROM:", TWILIO_FROM)


twilio_client = None
if TWILIO_SID and TWILIO_TOKEN:
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)



# ============================================================
# 1. Load CatBoost model + metadata
# ============================================================

BASE_DIR = Path(__file__).resolve().parent / "ml"

MODEL_PATH = BASE_DIR / "catboost_no_show_model.pkl"
FEATURES_PATH = BASE_DIR / "catboost_feature_list.pkl"
CATCOLS_PATH = BASE_DIR / "catboost_categorical_columns.pkl"
THRESHOLD_PATH = BASE_DIR / "catboost_best_threshold.pkl"

model = None
MODEL_FEATURES = None
CATEGORICAL_COLS = None
BEST_THRESHOLD = 0.50

try:
    model = joblib.load(MODEL_PATH)
    MODEL_FEATURES = joblib.load(FEATURES_PATH)
    CATEGORICAL_COLS = joblib.load(CATCOLS_PATH)
    BEST_THRESHOLD = joblib.load(THRESHOLD_PATH)
    print("✅ CatBoost model + metadata loaded successfully")
except Exception as e:
    print("⚠️ Failed to load CatBoost ML files:", e)



# ============================================================
# 2. Age band calculator
# ============================================================

def compute_age_band(dob, appt_date):
    if not dob:
        return "31-50"

    years = appt_date.year - dob.year
    if (appt_date.month, appt_date.day) < (dob.month, dob.day):
        years -= 1

    if years < 18:
        return "0-17"
    if years <= 30:
        return "18-30"
    if years <= 50:
        return "31-50"
    if years <= 70:
        return "51-70"
    return "70+"


def build_feature_row(user, appointment):
    if MODEL_FEATURES is None:
        return None

    appt_date = appointment.appointment_date

    # MAKE APPOINTMENT DATETIME AWARE
    appt_dt = timezone.make_aware(
        datetime.combine(appt_date, datetime.min.time())
    )

    # Start with a dict containing ALL model features initialized to safe defaults
    row = {f: 0 for f in MODEL_FEATURES}

    # -------------------------
    # TIME FEATURES
    # --------------------------
    # hour from slot if possible
    slot = AppointmentSlot.objects.filter(id=appointment.slot_id).first()
    row["hour"] = slot.start_time.hour if slot else 9

    row["day_of_week"] = appt_dt.weekday()
    row["appointment_day_of_month"] = appt_dt.day
    row["appointment_month"] = appt_dt.month
    row["appointment_weekofyear"] = appt_dt.isocalendar().week
    # row["appointment_day_name"] = appt_dt.strftime("%A")
    row["appointment_day_of_week_name"] = appt_dt.strftime("%A")


    # lead time
    if appointment.created_at:
        row["lead_time_days"] = max((appt_dt - appointment.created_at).days, 0)
    else:
        row["lead_time_days"] = 7

    # -------------------------
    # IMD FIELDS
    # -------------------------
    postcode = getattr(user, "post_code", "") or ""
    imd_score, imd_band = lookup_imd(postcode)

    row["postcode"] = postcode
    row["imd_score"] = imd_score
    row["imd_band"] = imd_band

    # -------------------------
    # PATIENT FIELDS
    # -------------------------
    # age band
    dob = getattr(user, "date_of_birth", None)
    row["age_band"] = compute_age_band(dob, appt_date)

    # sex
    row["sex"] = getattr(user, "sex", "other")

    # chronic conditions
    chronic = (getattr(user, "chronic_condition", "") or "").lower()
    if chronic in ["", "none", "no"]:
        row["num_chronic_conditions"] = 0
        row["has_chronic"] = 0
        row["chronic_condition"] = "none"
    else:
        row["num_chronic_conditions"] = 1
        row["has_chronic"] = 1
        row["chronic_condition"] = chronic

    # -------------------------
    # APPOINTMENT HISTORY
    # -------------------------
    past = Appointment.objects.filter(patient=user, appointment_date__lt=appt_date)

    row["past_appointments"] = past.count()
    row["past_no_shows"] = 0
    row["attendance_rate"] = 1.0
    row["last_attended_days_ago"] = 30

    # -------------------------
    # DEFAULT FIELDS REQUIRED BY MODEL
    # -------------------------
    row["cancellations"] = 0
    row["late_arrivals"] = 0
    row["was_rescheduled"] = 0
    row["reschedule_count"] = 0
    row["distance_km"] = 5.0

    # reminders (before sending)
    row["sms_sent"] = 0
    row["sms_read"] = 0
    row["email_sent"] = 0
    row["call_attempted"] = 0

    # context features
    row["weather"] = "sunny"
    row["transport_disruption"] = 0
    row["local_holiday"] = 0

    # booking details
    row["booking_channel"] = "web"
    row["appointment_type"] = "checkup"

    # -------------------------
    # BUILD FINAL DATAFRAME EXACTLY IN CORRECT ORDER
    # -------------------------
    df = pd.DataFrame([[row[f] for f in MODEL_FEATURES]], columns=MODEL_FEATURES)

    # convert categorical fields to strings
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str)

    print("🔍 FINAL FEATURE ROW:", df.to_dict(orient="records")[0])
    print("DEBUG postcode used for IMD:", postcode)
    return df

def ml_predict_no_show_probability(user, appointment):
    # 1) Check model
    if model is None:
        print("❌ DEBUG: model is None inside ml_predict_no_show_probability")
        return None

    # 2) Build features
    features = build_feature_row(user, appointment)

    if features is None:
        print("❌ DEBUG: build_feature_row returned None")
        print("   DEBUG: MODEL_FEATURES =", MODEL_FEATURES)
        return None

    print("✅ DEBUG: model and features are OK")
    print("   DEBUG: features columns =", list(features.columns))

    try:
        proba = model.predict_proba(features)[0, 1]
        print("✅ DEBUG: raw model probability =", proba)
        return float(proba)
    except Exception as e:
        print("⚠️ DEBUG: prediction error:", repr(e))
        return None

def predict_risk_and_intervention(user, appointment):
    p = ml_predict_no_show_probability(user, appointment)
    print("🔥 ML SCORE (no-show probability) =", p)

    if p is None:
        print("⚠️ ML model returned None — fallback activated")
        import random
        risk = random.choice(["low", "medium", "high"])
    else:
        if p < 0.30:
            risk = "low"
        elif p < 0.60:
            risk = "medium"
        else:
            risk = "high"

        print(f"📌 ML Probability = {p:.3f} → Risk = {risk}")

    if risk == "low":
        intervention = "sms"
    elif risk == "medium":
        intervention = "sms_confirm"
    else:
        intervention = "sms_call"

    return risk, intervention

# Automated intervention
import re

def normalize_phone(phone):
    if not phone:
        return None

    p = re.sub(r"\s+", "", phone)

    if p.startswith("+"):
        return p
    if p.startswith("0"):
        return "+44" + p[1:]
    if p.startswith("44"):
        return "+44" + p[2:]

    return p

def send_sms(to, message):
    if not twilio_client:
        print("❌ SMS not sent — Twilio not configured")
        return False

    to = normalize_phone(to)
    if not to or not to.startswith("+"):
        print("❌ Invalid phone number:", to)
        return False

    try:
        msg = twilio_client.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=to
        )
        print("📩 SMS SENT:", msg.sid, "to", to)
        return True
    except Exception as e:
        print("❌ SMS FAILED:", e)
        return False

def send_reminder_for_appointment(appointment):
    user = appointment.patient
    phone = normalize_phone(getattr(user, "phone", None))

    if not phone:
        print(f"❌ No phone for {user.email}")
        return

    risk = appointment.risk_level
    date_str = appointment.appointment_date.strftime("%Y-%m-%d")

    print(f"🔔 Reminder triggered for {user.email} | risk={risk}")

    if risk == "low":
        send_sms(
            phone,
            f"Reminder: You have an NHS appointment tomorrow ({date_str})."
        )

    elif risk == "medium":
        send_sms(
            phone,
            f"Please confirm your NHS appointment tomorrow ({date_str}) by replying YES."
        )

    elif risk == "high":
        # Call first (placeholder)
        call_answered = False  # integrate Twilio call later

        if not call_answered:
            send_sms(
                phone,
                f"We tried to reach you by phone. "
                f"Please attend your NHS appointment tomorrow ({date_str})."
            )
