# # # appointments/services.py
# # import random

# # def fake_predict_risk_and_intervention(patient, appointment):
# #     """
# #     TEMPORARY placeholder.
# #     Later you'll load your trained model and use real features.
# #     """

# #     # Example simple rule:
# #     # - If patient has many past no-shows -> higher risk
# #     # - For now we just randomise for testing

# #     choices = ["low", "medium", "high"]
# #     risk = random.choice(choices)

# #     if risk == "low":
# #         intervention = "sms"           # simple SMS
# #     elif risk == "medium":
# #         intervention = "sms_confirm"   # SMS that requires YES/NO reply
# #     else:
# #         intervention = "sms_call"      # SMS + automated call

# #     return risk, intervention

# # appointments/services.py

# import os
# from pathlib import Path
# from datetime import datetime

# import numpy as np
# import pandas as pd
# import joblib

# # ==========================
# # 1. Load model + feature list
# # ==========================

# BASE_DIR = Path(__file__).resolve().parent

# MODEL_PATH = BASE_DIR / "ml" / "xgb_no_show_model_final.pkl"
# FEATURES_PATH = BASE_DIR / "ml" / "model_features_final.pkl"

# model = None
# MODEL_FEATURES = None

# try:
#     model = joblib.load(MODEL_PATH)
#     MODEL_FEATURES = joblib.load(FEATURES_PATH)
#     print("✅ Loaded no-show model and features.")
# except Exception as e:
#     print("⚠️ Could not load ML model, falling back to random:", e)


# # Your tuned F1 threshold for class 1 (no-show)
# BEST_THRESHOLD = 0.50801337


# # ==========================
# # 2. Build feature vector from appointment + user
# # ==========================

# def build_feature_row(patient, appointment):
#     """
#     Build a single-row feature vector that matches MODEL_FEATURES.

#     Important note:
#     - The model was trained on a rich Kaggle dataset with many fields
#       (Age, Scholarship, Neighbourhood dummies, etc).
#     - Your current Django models don't have all those fields.
#     - To keep the system running, we initialise all features to 0
#       and fill only what we can (waiting_days, day-of-week, etc).
#     - This is enough for demonstrating integration and end-to-end flow
#       for your dissertation, but in production you would align your
#       database schema with the training features.
#     """

#     if MODEL_FEATURES is None:
#         # fallback: just return None and let caller handle it
#         return None

#     # Start with zeros for every feature
#     data = {feature_name: 0 for feature_name in MODEL_FEATURES}

#     # ----- Derive what we can from Appointment + User -----

#     # waiting_days = days between scheduled and appointment
#     # we'll approximate "ScheduledDay" as created_at (when booked in your system)
#     if hasattr(appointment, "created_at") and appointment.created_at:
#         scheduled_dt = appointment.created_at
#     else:
#         scheduled_dt = datetime.now()

#     appointment_dt = datetime.combine(appointment.appointment_date, datetime.min.time())
#     waiting_days = (appointment_dt - scheduled_dt).days
#     waiting_days = max(waiting_days, 0)

#     if "waiting_days" in data:
#         data["waiting_days"] = waiting_days

#     # Day of week (0=Mon, ..., 6=Sun)
#     appt_day_of_week = appointment_dt.weekday()
#     if "Appt_DayOfWeek" in data:
#         data["Appt_DayOfWeek"] = appt_day_of_week

#     # Weekend flag
#     is_weekend = 1 if appt_day_of_week in [5, 6] else 0
#     if "Appt_is_weekend" in data:
#         data["Appt_is_weekend"] = is_weekend

#     # Month
#     if "Appt_Month" in data:
#         data["Appt_Month"] = appointment_dt.month

#     # Hour – your Appointment model doesn’t store time, only date.
#     # If in future you add a real TimeField or slot relationship, use that.
#     # For now we default to 9am to keep it consistent.
#     default_hour = 9
#     if "Appt_Hour" in data:
#         data["Appt_Hour"] = default_hour

#     # Age / AgeGroup – if you later store date_of_birth or age on the user,
#     # you can compute it here. For now we leave them at 0.

#     # Example if you later add patient.age to your User model:
#     # if hasattr(patient, "age") and "Age" in data:
#     #     data["Age"] = patient.age

#     # Convert to DataFrame with 1 row and columns in correct order
#     row_df = pd.DataFrame([[data[col] for col in MODEL_FEATURES]], columns=MODEL_FEATURES)
#     return row_df


# # ==========================
# # 3. Core predictor
# # ==========================

# def ml_predict_no_show_probability(patient, appointment):
#     """
#     Returns probability that this appointment is a no-show (class 1).
#     """
#     if model is None or MODEL_FEATURES is None:
#         return None  # caller will fallback

#     features_df = build_feature_row(patient, appointment)
#     if features_df is None:
#         return None

#     # Predict probability for class 1 (no-show)
#     proba = model.predict_proba(features_df)[0, 1]
#     return float(proba)


# # ==========================
# # 4. Public function used by your views
# # ==========================

# import random


# def predict_risk_and_intervention(patient, appointment):
#     """
#     Main function your views should call.

#     1) Tries to use the trained XGBoost model.
#     2) If model is unavailable, falls back to random (so nothing breaks).
#     3) Maps probability → risk band → intervention type.
#     """

#     p_no_show = ml_predict_no_show_probability(patient, appointment)

#     if p_no_show is None:
#         # Fallback to the old fake logic if the model can't be used
#         print("⚠️ Using random fallback for risk prediction.")
#         choices = ["low", "medium", "high"]
#         risk = random.choice(choices)

#     else:
#         # Threshold for class 1 is ~0.508 (F1-optimised)
#         # We can define bands around that to get low/medium/high.
#         if p_no_show < 0.3:
#             risk = "low"
#         elif p_no_show < 0.7:
#             risk = "medium"
#         else:
#             risk = "high"

#         print(f"Predicted no-show probability={p_no_show:.3f}, risk={risk}")

#     # Map risk → intervention policy
#     if risk == "low":
#         intervention = "sms"           # simple SMS
#     elif risk == "medium":
#         intervention = "sms_confirm"   # SMS that requires confirmation
#     else:
#         intervention = "sms_call"      # SMS + call

#     return risk, intervention


# appointments/services.py

import os
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import joblib

# ====================================
# 1. Load CatBoost model + metadata
# ====================================

BASE_DIR = Path(__file__).resolve().parent / "ml"

MODEL_PATH = BASE_DIR / "catboost_no_show_model.pkl"
FEATURES_PATH = BASE_DIR / "catboost_feature_list.pkl"
CATEGORICAL_PATH = BASE_DIR / "catboost_categorical_columns.pkl"
THRESHOLD_PATH = BASE_DIR / "catboost_best_threshold.pkl"

model = None
MODEL_FEATURES = None
CATEGORICAL_COLS = None
BEST_THRESHOLD = 0.5   # fallback, replaced when file loads

try:
    model = joblib.load(MODEL_PATH)
    MODEL_FEATURES = joblib.load(FEATURES_PATH)
    CATEGORICAL_COLS = joblib.load(CATEGORICAL_PATH)
    BEST_THRESHOLD = joblib.load(THRESHOLD_PATH)

    print("✅ CatBoost model + metadata loaded successfully")

except Exception as e:
    print("⚠️ Could not load CatBoost files:", e)



# ====================================
# 2. Build the ML feature row
# ====================================

def build_feature_row(patient, appointment):
    """
    Convert appointment + user data into a single-row DataFrame
    matching MODEL_FEATURES from the CatBoost training pipeline.
    """

    if MODEL_FEATURES is None:
        return None

    # initialize dictionary for all features
    row = {feature: 0 for feature in MODEL_FEATURES}

    # -------------------------------
    # Populate available features
    # -------------------------------

    appt_date = appointment.appointment_date
    appt_datetime = datetime.combine(appt_date, datetime.min.time())

    # Lead time (days between booking and appointment)
    if appointment.created_at:
        delta = appt_datetime - appointment.created_at
        row["lead_time_days"] = max(delta.days, 0)

    # Day of week (0–6)
    row["day_of_week"] = appt_datetime.weekday()

    # Day of month
    row["appointment_day_of_month"] = appt_datetime.day

    # Default appointment hour (you can replace with slot start_time later)
    row["hour"] = 9

    # Example mapping from patient fields (if you added them):
    try:
        row["age_band"] = getattr(patient, "age_band", "18-30")
        row["sex"] = getattr(patient, "sex", "other")
        row["rurality"] = getattr(patient, "rurality", "urban")
        row["chronic_condition"] = getattr(patient, "chronic_condition", "none")
        row["num_chronic_conditions"] = int(getattr(patient, "num_chronic_conditions", 0))

    except Exception:
        pass

    # Convert to DataFrame
    df = pd.DataFrame([row])

    # Ensure categorical columns are strings
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # Ensure correct order
    df = df[MODEL_FEATURES]

    return df



# ====================================
# 3. Core predictor
# ====================================

def ml_predict_no_show_probability(patient, appointment):
    """Return probability (0–1) that the patient will miss the appointment."""
    
    if model is None or MODEL_FEATURES is None:
        return None

    features_df = build_feature_row(patient, appointment)
    if features_df is None:
        return None

    proba = model.predict_proba(features_df)[0, 1]  # class 1 = no-show
    return float(proba)



# ====================================
# 4. Map prob → risk band → intervention
# ====================================

def predict_risk_and_intervention(patient, appointment):
    """
    Compute risk level + intervention strategy.
    """

    p = ml_predict_no_show_probability(patient, appointment)

    if p is None:
        # fallback (model missing)
        import random
        risk = random.choice(["low", "medium", "high"])
    else:
        # Probability-based banding
        if p < 0.30:
            risk = "low"
        elif p < 0.70:
            risk = "medium"
        else:
            risk = "high"

        print(f"🎯 ML Probability = {p:.3f} → Risk = {risk}")

    # map risk to intervention strategy
    if risk == "low":
        intervention = "sms"
    elif risk == "medium":
        intervention = "sms_confirm"
    else:
        intervention = "sms_call"

    return risk, intervention
