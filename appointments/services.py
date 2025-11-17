# appointments/services.py
import random

def fake_predict_risk_and_intervention(patient, appointment):
    """
    TEMPORARY placeholder.
    Later you'll load your trained model and use real features.
    """

    # Example simple rule:
    # - If patient has many past no-shows -> higher risk
    # - For now we just randomise for testing

    choices = ["low", "medium", "high"]
    risk = random.choice(choices)

    if risk == "low":
        intervention = "sms"           # simple SMS
    elif risk == "medium":
        intervention = "sms_confirm"   # SMS that requires YES/NO reply
    else:
        intervention = "sms_call"      # SMS + automated call

    return risk, intervention
