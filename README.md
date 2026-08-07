# panasonic-ac-models

A model capability database and lookup engine for Panasonic Air Conditioners (Indian Market). Covers both **Wi-Fi / MirAIe smart models** and **IR remote-only models**, providing hardware feature flags for HVAC integrations, Home Assistant custom integrations, companion libraries, and dashboard cards.

---

## Installation & Usage

### Python Library (Backend / Home Assistant Integrations)

Install via `pip`:

```bash
pip install panasonic-ac-models
```

Query feature gating flags using the normalized lookup engine:

```python
from panasonic_ac_models import ACModelLookup

lookup = ACModelLookup()

# Query capability dictionary for any indoor SKU.
# Handles CS-CU-, CS/CU-, CU-, lowercase, and whitespace variants automatically.
caps = lookup.get_capabilities("CS-CU-EU18CKY5XFM")

print(f"Model Series: {caps['series']} (Gen {caps['generation']})")
print(f"Family Key:   {caps['family_key']}")

# -------------------------------------------------------------
# 1. Route by Integration Type
# -------------------------------------------------------------

# --- Option A: MirAIe-only integration (skip IR models) ---
if caps["has_wifi"] == 0:
    raise ValueError(f"Model {caps['family_key']} is IR-only, not supported by MirAIe.")
setup_miraie_entities(caps)  # proceed with cloud/MQTT setup

# --- Option B: IR-only integration (skip Wi-Fi models) ---
if caps["has_wifi"] == 1:
    raise ValueError(f"Model {caps['family_key']} is Wi-Fi smart — use the MirAIe integration instead.")
setup_ir_entities(caps)  # proceed with IR blaster command setup

# --- Option C: Hybrid integration (support both) ---
if caps["has_wifi"] == 1:
    print("-> Wi-Fi Smart AC: Expose MirAIe cloud & MQTT entities.")
    setup_miraie_entities(caps)
else:
    print("-> IR Remote AC: Route to IR blaster command pipeline.")
    setup_ir_entities(caps)

# -------------------------------------------------------------
# 2. Gate HVAC Modes (Common: cool, dry, fan_only, auto, off; EZ/KZ add heat)
# -------------------------------------------------------------
common_hvac_modes = ["cool", "dry", "fan_only", "auto", "off"]

if caps["has_heat_mode"] == 1:
    hvac_modes = common_hvac_modes + ["heat"]  # EZ & KZ series dual heat pump
else:
    hvac_modes = common_hvac_modes             # Cooling-only unit

# -------------------------------------------------------------
# 3. Gate Nanoe Air Purification Switch
# -------------------------------------------------------------
if caps["has_nanoe"] == 1:
    show_nanoe_switch = True   # Expose Nanoe-G / Nanoe-X switch entity (HU & XU series only)
else:
    show_nanoe_switch = False  # Hide Nanoe switch entity

# -------------------------------------------------------------
# 4. Gate Converti Capacity Presets (7-in-1 / 8-in-1 / none)
# -------------------------------------------------------------
converti = caps["converti_type"]

if converti == "8-in-1":
    converti_presets = ["cv_110", "cv_100", "cv_90", "cv_80", "cv_70", "cv_60", "cv_50", "cv_40"]
elif converti == "7-in-1":
    converti_presets = ["cv_110", "cv_100", "cv_90", "cv_80", "cv_70", "cv_55", "cv_40"]
else:  # "none" -> Pre-2023 auto-convertible, fixed-speed, or IR-only: hide converti presets
    converti_presets = []
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
    const rawModel = "CS-CU-NU18AKY4WXD";

    // Normalize prefix variants (CS-CU-, CS/CU-, CU-, lowercase)
    const cleanModel = rawModel
      .trim()
      .toUpperCase()
      .replace(/^(CS[-_\/\s]?CU|CS\/CU|CS|CU)[-_\s]?/, "CS-");

    const family = data.families.find(f => f.indoor_units.includes(cleanModel));

    if (!family) {
      console.warn("Model not found in database.");
      return;
    }

    // Filter by integration type
    const isWifi = family.has_wifi === 1;
    console.log("Integration type:", isWifi ? "Wi-Fi / MirAIe Cloud" : "IR Remote Blaster");

    // Feature flags
    console.log("Heat Mode:", family.has_heat_mode === 1);
    console.log("Nanoe Ionizer:", family.has_nanoe === 1);
    console.log("Converti Mode:", family.converti_type);

    // Example: get all families for a Wi-Fi-only integration
    const wifiOnlyFamilies = data.families.filter(f => f.has_wifi === 1);
    console.log("Total Wi-Fi smart families:", wifiOnlyFamilies.length);

    // Example: get all families for an IR-only integration
    const irOnlyFamilies = data.families.filter(f => f.has_wifi === 0);
    console.log("Total IR remote families:", irOnlyFamilies.length);
  });
```

---

## Feature Gating Rules

| Feature | Applies To | Series / Condition |
|---|---|---|
| **Wi-Fi / MirAIe Smart** | Inverter splits & smart window ACs | NU, SU (W/WD/WF variants), EU, AU, HU, XU, EZ, KZ, WU, QU, YU, RU-C, TU, VU, ZU, LU, KU, LN (inverter), XU (window), PU (commercial smart), PB (commercial tower) |
| **IR Remote Only** | Fixed-speed & non-smart models | KN (fixed-speed splits), XN (fixed-speed window ACs), LN-C (fixed-speed window ACs), RU-A/B, SU titanium panel variants (T/TD/TF/TK suffix), PD, PU-5 (older commercial) |
| **Heat Mode** | Dual heat pump series | EZ and KZ series only |
| **Nanoe Ionizer** | Air purification premium series | HU and XU series only |
| **Nanoe-X (Commercial)** | Commercial heat pump cassettes | PU Gen 6/7/8, PB commercial tower |
| **Converti 8-in-1** | 2026+ generation models | NU/SU/WU/QU (Gen ≥ B) and EZ/HU/EU/AU (Gen ≥ C) |
| **Converti 7-in-1** | 2023–2025 generation models | All other 2023–2025 inverter splits |
| **No Converti** | Pre-2023 or fixed-speed / commercial | Gen W, X (sensor auto-scaling), all IR-only models, all commercial cassettes |

---

## Database Summary

- **Models Tracked**: 486 models across 144 hardware families.
  - **398 Wi-Fi / MirAIe Smart models** across 115 families — for cloud/MQTT integrations.
  - **88 IR Remote-Only models** across 29 families — for IR blaster integrations.
- **Data Sources**: Bureau of Energy Efficiency (BEE) certified labels, Panasonic India catalogs, empirical MirAIe telemetry, and live retail verification.

---

## Contributing

Pull requests are welcome! To add or correct a model:

1. Edit `models.json`.
2. Add the indoor SKU to the appropriate `indoor_units` array under `families`.
3. Set `has_wifi: 0` for IR-only models, `has_wifi: 1` for Wi-Fi smart models.
4. Submit a PR. Continuous Integration (`check-jsonschema`) will validate changes against `schema.json`.

---

## Authors & Credits

- **Lead Maintainer**: [@selvakk2k](https://github.com/selvakk2k)
- **AI Pair Programming & Architecture**: Antigravity (Google DeepMind Team)
