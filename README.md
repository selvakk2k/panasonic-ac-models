# 🌐 Panasonic AC Model Masterlist (`panasonic-ac-models`)

An open, community-driven hardware database and feature gating reference for **Panasonic Smart Air Conditioners (Indian Market / MirAIe IoT Platform)**.

Designed for Home Assistant custom integrations (`ha-miraie-ac-in`), companion libraries (`miraie-ac-in`), custom Lovelace cards, Blueprints, and home automation tools.

---

## 👥 Authors & Credits

Maintained collaboratively by:
- **Lead Architect & Maintainer** — [@selvakk2k](https://github.com/selvakk2k)
- **Antigravity (Google DeepMind Team)** — AI Pair Programmer, Database Architecture & Empirical Gating Verification.

See `manifest.json` for full metadata.

---

## 🚀 CDN Direct Usage (Fast & Open)

You can fetch the master JSON dataset directly in JavaScript, Python, or Jinja templates via jsDelivr CDN:

```
https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json
```

### Example: JavaScript / Card-Mod
```js
fetch("https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json")
  .then(response => response.json())
  .then(data => {
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
3. Submit a Pull Request! GitHub Actions will validate your PR against `schema.json`.

---

*Maintained by the Open MirAIe Community*
