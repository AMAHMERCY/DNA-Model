def send_sms(phone, message):
    print(f"📩 SMS sent to {phone}: {message}")
    return True


def send_confirm_sms(phone, message):
    print(f"✅ CONFIRM SMS sent to {phone}: {message}")
    return True


def make_automated_call(phone, message):
    print(f"📞 CALL placed to {phone}: {message}")
    # simulate call not answered 50% of the time
    import random
    return random.choice([True, False])  # True = answered
