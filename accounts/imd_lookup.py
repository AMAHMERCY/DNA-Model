IMD_TABLE = {
    # ---- Manchester Central (high deprivation) ----
    "M1": 3, "M2": 3, "M3": 2, "M4": 2, "M5": 3, "M6": 2, "M7": 3,
    "M8": 2, "M9": 1, "M11": 2, "M12": 2, "M13": 2, "M14": 1,
    "M15": 2, "M16": 3, "M18": 2, "M19": 3, "M40": 2,

    # ---- Mixed areas (medium deprivation) ----
    "M20": 6, "M21": 5, "M22": 5, "M23": 6, "M24": 5, "M25": 6,
    "M26": 5, "M27": 5, "M28": 6, "M30": 6, "M31": 6,

    # ---- Lower deprivation suburbs / nearby towns ----
    "M32": 7, "M33": 8, "M34": 6, "M35": 7, "M38": 7, "M41": 8,
    "M43": 7, "M44": 7, "M45": 8, "M46": 7,

    # ---- Stockport, Trafford, Warrington (wealthier areas) ----
    "SK1": 7, "SK2": 8, "SK3": 8, "SK4": 9, "SK5": 7, "SK6": 9,
    "SK7": 9, "SK8": 8, "SK9": 10,

    "WA1": 7, "WA2": 6, "WA3": 7, "WA4": 9, "WA5": 7,
    "WA13": 10, "WA14": 10, "WA15": 9,


    "OL1": 4, "OL2": 5, "OL3": 6, "OL4": 4, "OL5": 5, "OL6": 4,
    "BL1": 6, "BL2": 6, "BL3": 5, "BL4": 5, "BL5": 6,
}


def _imd_band(score: int) -> str:
    """
    1–3  = high deprivation
    4–7  = medium
    8–10 = low
    """
    if score <= 3:
        return "high"
    elif score <= 7:
        return "medium"
    return "low"


def lookup_imd(postcode: str):
    """
    Given full postcode (e.g. 'M14 7HF') return (imd_score, imd_band).
    If prefix unknown → fall back to medium deprivation (score=5).
    """
    if not postcode:
        score = 5
        return score, _imd_band(score)

    pc = postcode.strip().upper().replace(" ", "")
    prefix3 = pc[:3]
    prefix2 = pc[:2]

    if prefix3 in IMD_TABLE:
        score = IMD_TABLE[prefix3]
        return score, _imd_band(score)

    if prefix2 in IMD_TABLE:
        score = IMD_TABLE[prefix2]
        return score, _imd_band(score)

    score = 5
    return score, _imd_band(score)
