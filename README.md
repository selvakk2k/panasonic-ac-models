# 🌐 Panasonic AC Model Masterlist (`panasonic-ac-models`)

An open, community-driven hardware database and feature gating reference for **Panasonic Smart Air Conditioners (Indian Market / MirAIe IoT Platform)**.

Designed for Home Assistant custom integrations, companion libraries, custom Lovelace cards, Blueprints, and home automation tools.

---

## 🚀 Installation & Direct CDN Usage

You can consume the master database either as a Python client package or directly via jsDelivr CDN:

### 1. Direct CDN URL (JavaScript / Lovelace Cards)
```
https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json
```

### 2. Python Package (`panasonic_ac_models`)
```bash
pip install git+https://github.com/selvakk2k/panasonic-ac-models.git
```

---

## 💻 How to Use in Your Project

### Option A: Using the Python Client Package (Recommended for Backend Integrations)

The `panasonic_ac_models` Python package provides an $O(1)$ lookup engine with automatic prefix normalization (`CS/CU-` ➔ `CS-`, casing/whitespace tolerance) and deterministic regex fallback decoding for unindexed SKUs:

```python
from panasonic_ac_models import ACModelLookup

# 1. Initialize lookup engine (loads models.json)
lookup = ACModelLookup()

# 2. Lookup capabilities for any model variation
caps = lookup.get_capabilities("CS/CU-EZ18BKYD")

print("Series:", caps["series"])                # "EZ"
print("Heat Mode:", caps["has_heat_mode"])     # 1 (Dual Hot & Cold)
print("Nanoe:", caps["has_nanoe"])             # 0
print("Converti Mode:", caps["converti_type"]) # "7-in-1"

# 3. Gate your integration features dynamically!
hvac_modes = ["cool", "heat", "off"] if caps["has_heat_mode"] == 1 else ["cool", "off"]
show_nanoe = (caps["has_nanoe"] == 1)

if caps["converti_type"] == "8-in-1":
    presets = ["cv_110", "cv_100", "cv_90", "cv_80", "cv_70", "cv_60", "cv_50", "cv_40"]
elif caps["converti_type"] == "7-in-1":
    presets = ["cv_110", "cv_100", "cv_90", "cv_80", "cv_70", "cv_55", "cv_40"]
else:
    presets = []  # "none" -> Hide converti presets
```

---

### Option B: Direct CDN Fetch (JavaScript / Lovelace Cards)

Frontend cards can fetch `models.json` directly via CDN to dynamically show or hide UI controls:

```js
fetch("https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json")
  .then(response => response.json())
  .then(data => {
    // Find model family by indoor unit model code
    const family = data.families.find(f => f.indoor_units.includes("CS-NU18AKY4WXD"));
    console.log("Heat Mode:", family.has_heat_mode);      // 0
    console.log("Nanoe:", family.has_nanoe);              // 0
    console.log("Converti Mode:", family.converti_type);  // "7-in-1"
  });
```

---

## 📌 Feature Gating Matrix (Empirically Verified)

| Feature | Gating Condition | Target Series / Generations |
|---|---|---|
| 📶 **Wi-Fi / MirAIe** | All Inverter Split Series | `NU`, `SU`, `EU`, `AU`, `HU`, `XU`, `EZ`, `KZ`, `WU`, `QU`, `YU`, `RU`, `TU`, `VU`, `ZU`, `LU`, `S-##PUY` |
| ❌ **Non-Smart** | Fixed Speed, Window ACs, Entry Inverters | `KN` (Fixed), `KU` (Entry Inverter), `CW-` (Window), `PUB`/`PD` (Fixed Cassettes) |
| 🔥 **Heat Mode (Hot & Cold)** | Dual Heat Pump Series | **`EZ`** and **`KZ`** series **ONLY** |
| 🌿 **Nanoe Air Purification** | Active Ionizer Series | **`HU`** (Amaze Grey) and **`XU`** series **ONLY** |
| ⚡ **Converti 8-in-1** | 2026+ Gen B/C Models | `NU`/`SU` (Gen ≥ B) & `EZ`/`HU`/`EU` (Gen ≥ C) |
| ⚡ **Converti 7-in-1** | 2023–2025 Gen Y/Z/A Models | All other smart inverter split models (2023–2025) |
| 🔄 **Auto-Convertible / None (`none`)** | Pre-2023 & Non-Smart Lines | 2020–2022 models (Gen W, X - Auto-Convertible sensor scaling only; no manual preset buttons), `KN`, `KU`, `CW-`, `PUB`, `PD` |

---

## ℹ️ Auto-Convertible vs. Manual Converti (Pre-2023 vs 2023+)

* **2020–2022 Models (Generations W & X)**: Featured **Auto-Convertible** inverter technology. The AC automatically modulates compressor frequency using internal sensors, but **does not have manual percentage buttons** (40%, 70%, 100%) on the remote or MirAIe app. These are set to `converti_type: "none"` so Home Assistant does not show unsupported manual preset buttons.
* **2023–2025 Models (Generations Y, Z, A)**: Featured manual **Converti 7-in-1** (`converti_type: "7-in-1"`).
* **2026+ Models (Generations B, C)**: Upgraded to **Converti 8-in-1** (`converti_type: "8-in-1"`).

---

## 📊 Database Summary

* **Total Verified Wi-Fi Smart Models**: **403 models**
* **Total Unique Hardware Families**: **116 families**
* **Data Sources**: Bureau of Energy Efficiency (BEE) Certified Label Database + Panasonic India Product Catalogs + Empirical Web Verification.

---

## 🤝 Contributing / Adding New Models

We welcome community pull requests! To add or update a model:

1. Edit `models.json`.
2. Add your indoor unit model number under the appropriate `indoor_units` array in `families`.
3. Submit a Pull Request! GitHub Actions will validate your PR automatically against `schema.json`.

---

## 👥 Authors & Credits

Maintained collaboratively by:
- **Lead Architect & Maintainer** — [@selvakk2k](https://github.com/selvakk2k)
- **Antigravity (Google DeepMind Team)** — AI Pair Programmer, Database Architecture & Empirical Gating Verification.

See `manifest.json` for full metadata.
