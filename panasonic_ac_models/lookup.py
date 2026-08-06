import json
import os
import re
from typing import Dict, Any, Optional
from .decoder import decode_model_string

DEFAULT_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models.json"
)


def normalize_code(raw_code: str) -> str:
    """Normalizes input model strings (e.g. 'cs/cu-su18aky3w' -> 'CS-SU18AKY3W')."""
    cleaned = raw_code.strip().upper()
    cleaned = re.sub(r'^(CS/CU|CU)[-_\s]?', 'CS-', cleaned)
    if not cleaned.startswith('CS-') and not cleaned.startswith('S-'):
        cleaned = f"CS-{cleaned}"
    return cleaned


class ACModelLookup:
    """O(1) normalized lookup engine for Panasonic AC models."""

    def __init__(self, json_path: Optional[str] = None):
        path = json_path or DEFAULT_JSON_PATH
        with open(path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

        # O(1) Normalized Lookup Index
        self._index: Dict[str, Dict[str, Any]] = {}
        for family in self.db.get("families", []):
            for unit in family.get("indoor_units", []):
                norm = normalize_code(unit)
                self._index[norm] = family

    def get_capabilities(self, model_code: str) -> Dict[str, Any]:
        """Resolves capability flags using exact index matching or regex decoding."""
        norm = normalize_code(model_code)

        # 1. Exact Match from Index
        if norm in self._index:
            result = dict(self._index[norm])
            result["resolved_via"] = "database"
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
