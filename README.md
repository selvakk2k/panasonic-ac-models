# panasonic-ac-models

A model capability database and lookup engine for Panasonic Smart Air Conditioners (Indian Market / MirAIe platform). Designed for Home Assistant custom integrations, companion libraries, and custom dashboard cards to dynamically determine supported AC features (HVAC modes, Nanoe ionizer, Converti presets).

---

## Installation & Usage

### Python Library (Backend / Home Assistant Integrations)

Install via `pip`:

```bash
pip install git+https://github.com/selvakk2k/panasonic-ac-models.git
```

Query AC capabilities using the normalized lookup engine:

```python
from panasonic_ac_models import ACModelLookup

lookup = ACModelLookup()

# Query any indoor unit SKU (handles 'CS/CU-', casing, and spaces automatically)
caps = lookup.get_capabilities("CS/CU-EZ18BKYD")

print(caps["series"])          # "EZ"
print(caps["has_heat_mode"])   # 1 (Dual Heat Pump)
print(caps["converti_type"])   # "7-in-1"

# Dynamic feature gating
hvac_modes = ["cool", "heat", "off"] if caps["has_heat_mode"] == 1 else ["cool", "off"]
show_nanoe = (caps["has_nanoe"] == 1)
```

---

### Direct CDN (JavaScript / Frontend Cards)

Fetch `models.json` directly via jsDelivr CDN:

```
https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json
```

```javascript
fetch("https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json")
  .then(res => res.json())
  .then(data => {
    const rawModel = "CS/CU-NU18AKY4WXD";
    const cleanModel = rawModel.replace(/^(CS\/CU|CU)[-_\s]?/i, 'CS-').trim().toUpperCase();
    
    const family = data.families.find(f => f.indoor_units.includes(cleanModel));
    console.log("Heat Mode:", family?.has_heat_mode);
    console.log("Converti Mode:", family?.converti_type);
  });
```

---

## Feature Gating Rules

| Feature | Condition | Series / Generations |
|---|---|---|
| Wi-Fi / MirAIe | All Inverter Splits | NU, SU, EU, AU, HU, XU, EZ, KZ, WU, QU, YU, RU, TU, VU, ZU, LU, S-##PUY |
| Non-Smart | Fixed Speed / Window | KN, KU, CW-, PUB, PD |
| Heat Mode | Dual Heat Pump | EZ, KZ only |
| Nanoe Ionizer | Purification Models | HU, XU only |
| Converti 8-in-1 | 2026+ Models | NU/SU (Gen ≥ B) & EZ/HU/EU (Gen ≥ C) |
| Converti 7-in-1 | 2023–2025 Models | All other 2023–2025 inverter splits |
| Auto-Convertible (none) | Pre-2023 Models | 2020–2022 models (Gen W, X - sensor auto-scaling, no manual percentage buttons) |

---

## Database Summary

- **Models Tracked**: 403 verified Wi-Fi models across 116 hardware families.
- **Data Sources**: Bureau of Energy Efficiency (BEE) certified labels, Panasonic India catalogs, empirical MirAIe telemetry.

---

## Contributing

Pull requests are welcome! To add or correct a model:

1. Edit `models.json`.
2. Add the indoor SKU to the appropriate `indoor_units` array under `families`.
3. Submit a PR. Continuous Integration (`check-jsonschema`) will validate changes against `schema.json`.

---

## Authors & Credits

- **Lead Maintainer**: [@selvakk2k](https://github.com/selvakk2k)
- **AI Pair Programming & Architecture**: Antigravity (Google DeepMind Team)
