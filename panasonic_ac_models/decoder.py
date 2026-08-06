import re
from typing import Dict, Any, Optional

PANASONIC_MODEL_REGEX = re.compile(
    r"^(?:CS/CU|CS|CU|S)?[-_\s]?"
    r"(?P<series>[A-Z]{2})"
    r"(?P<capacity>\d{2})"
    r"(?P<gen>[A-Z])"
    r"(?:KY)?"
    r"(?P<rating>\d)?"
    r"(?P<suffix>[A-Z0-9-]*)$",
    re.IGNORECASE
)

CAPACITY_MAP = {
    "09": "0.75T",
    "11": "0.9T",
    "12": "1T",
    "17": "1.4T",
    "18": "1.5T",
    "24": "2T",
    "26": "2.2T",
    "30": "2.5T",
}

HEAT_MODE_SERIES = {"EZ", "KZ"}
NANOE_SERIES = {"HU", "XU"}


def decode_model_string(model_code: str) -> Optional[Dict[str, Any]]:
    """Parses capability flags from a Panasonic AC model code string via deterministic rules."""
    match = PANASONIC_MODEL_REGEX.match(model_code.strip().upper())
    if not match:
        return None

    data = match.groupdict()
    series = data["series"]
    gen = data["gen"]

    # Converti Generation Logic: Gen >= B/C receives 8-in-1; Gen Y/Z/A receives 7-in-1; older -> none
    if gen in {"B", "C"}:
        converti = "8-in-1"
    elif gen in {"Y", "Z", "A"}:
        converti = "7-in-1"
    else:
        converti = "none"

    return {
        "family_key": f"{series}-{data['capacity']}-{gen}",
        "series": series,
        "generation": gen,
        "capacity_class": CAPACITY_MAP.get(data["capacity"], f"{data['capacity']} Ton"),
        "speed_type": "variable",
        "has_wifi": 1,
        "has_heat_mode": 1 if series in HEAT_MODE_SERIES else 0,
        "has_nanoe": 1 if series in NANOE_SERIES else 0,
        "converti_type": converti,
        "resolved_via": "regex_decoder"
    }
