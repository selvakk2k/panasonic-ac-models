import json
import os
import re
from typing import Dict, Any, Optional
from .decoder import decode_model_string

PKG_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(PKG_DIR)

DEFAULT_JSON_PATH = os.path.join(PKG_DIR, "models.json")
if not os.path.exists(DEFAULT_JSON_PATH):
    DEFAULT_JSON_PATH = os.path.join(PARENT_DIR, "models.json")

DEFAULT_BEE_PATH = os.path.join(PKG_DIR, "bee_data.json")
if not os.path.exists(DEFAULT_BEE_PATH):
    DEFAULT_BEE_PATH = os.path.join(PARENT_DIR, "bee_data.json")


def normalize_code(raw_code: str) -> str:
    """Normalizes input model strings across Split (CS-), Window (CW-), and Cassette (S-) formats."""
    cleaned = raw_code.strip().upper()
    
    # Window AC series (LN, XN, CW)
    if re.search(r'(?:CW|LN|XN)', cleaned):
        body = re.sub(r'^(CS[-_/\s]?CU|CS/CU|CS|CU|CW)[-_\s]?', '', cleaned)
        return f'CW-{body}'
        
    # Commercial Cassette / Ductable series (S-18PU..., S-24PD...)
    if cleaned.startswith('S-') or re.search(r'\d{2}P[UD]', cleaned):
        body = re.sub(r'^(CS[-_/\s]?CU|CS/CU|CS|CU|S)[-_\s]?', '', cleaned)
        return f'S-{body}'

    # Standard Split AC series (CS-)
    body = re.sub(r'^(CS[-_/\s]?CU|CS/CU|CS|CU)[-_\s]?', '', cleaned)
    return f'CS-{body}'


class ACModelLookup:
    """O(1) normalized lookup engine for Panasonic AC models."""

    def __init__(self, json_path: Optional[str] = None, bee_path: Optional[str] = None):
        path = json_path or DEFAULT_JSON_PATH
        with open(path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

        # O(1) Normalized Lookup Index
        self._index: Dict[str, Dict[str, Any]] = {}
        for family in self.db.get("families", []):
            for unit in family.get("indoor_units", []):
                norm = normalize_code(unit)
                self._index[norm] = family

        # O(1) Normalized BEE Star-Label Index
        self._bee_index: Dict[str, Dict[str, Any]] = {}
        b_path = bee_path or DEFAULT_BEE_PATH
        if os.path.exists(b_path):
            with open(b_path, "r", encoding="utf-8") as f:
                for row in json.load(f):
                    raw_model = row.get("model", "")
                    indoor = raw_model.split("/", 1)[0].strip()
                    if indoor:
                        self._bee_index[normalize_code(indoor)] = row

    def get_capabilities(self, model_code: str) -> Dict[str, Any]:
        """Resolves capability flags using exact index matching or regex decoding."""
        norm = normalize_code(model_code)

        # 1. Exact Match from Index
        if norm in self._index:
            result = dict(self._index[norm])
            result["resolved_via"] = "database"
            # Suffix-level override: -1 and -2 variants (e.g. CS-RU18CKY-1), plus SU-T series are non-Wi-Fi IR models
            if re.search(r'-(?:1|2)$', norm) or (result.get("series") == "SU" and re.search(r'T[A-Z0-9-]*$', norm)):
                result["has_wifi"] = 0
            return result

        # 2. Dynamic Fallback
        dynamic = decode_model_string(model_code)
        if dynamic:
            return dynamic

        # 3. Default Safe Fallback
        return {
            "family_key": "UNKNOWN",
            "has_wifi": 1,
            "has_heat_mode": 0,
            "has_nanoe": 0,
            "converti_type": "7-in-1",
            "resolved_via": "safe_default"
        }

    def get_bee_profile(self, model_code: str) -> Dict[str, Any]:
        """Resolve BEE star-label electrical and cooling characteristics for a model."""
        norm = normalize_code(model_code) if model_code else ""
        bee_row = self._bee_index.get(norm)
        source = "bee_database"

        if bee_row is not None:
            ton = float(bee_row.get("ton") or 1.5)
            iseer = float(bee_row.get("iseer") or 5.0)
            star_rating = int(bee_row.get("star_rating") or 3)
            annual_kwh = bee_row.get("annual_kwh")
        else:
            caps = self.get_capabilities(model_code) if model_code else {}
            cap_str = str(caps.get("capacity_class", "1.5T")).upper().replace("T", "")
            try:
                ton = float(cap_str)
            except ValueError:
                ton = 1.5
            iseer_min = caps.get("iseer_min")
            iseer_max = caps.get("iseer_max")
            if iseer_min and iseer_max:
                iseer = (float(iseer_min) + float(iseer_max)) / 2.0
            elif iseer_min or iseer_max:
                iseer = float(iseer_min or iseer_max)
            else:
                iseer = 5.0
            star_rating = int(caps.get("star_rating_max") or caps.get("star_rating_min") or 3)
            annual_kwh = None
            source = "family_derived" if caps.get("resolved_via") == "database" else "default_derived"

        rated_cooling_w = round(ton * 3516.85, 1)
        rated_power_w = round(rated_cooling_w / max(2.5, iseer * 0.595), 1)
        half_power_w = round((rated_cooling_w * 0.5) / max(3.0, iseer * 0.915), 1)
        min_power_w = round(half_power_w * 0.60, 1)

        return {
            "model": norm or model_code,
            "ton": ton,
            "star_rating": star_rating,
            "iseer": round(iseer, 2),
            "annual_kwh": annual_kwh,
            "rated_cooling_w": rated_cooling_w,
            "rated_power_w": rated_power_w,
            "half_power_w": half_power_w,
            "min_power_w": min_power_w,
            "resolved_via": source,
        }


_DEFAULT_LOOKUP: Optional[ACModelLookup] = None


def get_bee_profile(model_code: str) -> Dict[str, Any]:
    """Module-level helper to resolve BEE profile using the cached default lookup."""
    global _DEFAULT_LOOKUP
    if _DEFAULT_LOOKUP is None:
        _DEFAULT_LOOKUP = ACModelLookup()
    return _DEFAULT_LOOKUP.get_bee_profile(model_code)
