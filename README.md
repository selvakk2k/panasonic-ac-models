# Panasonic AC Hardware Profiles & IR Protocols (`panasonic-ac-models`)

[![Version](https://img.shields.io/github/v/release/selvakk2k/panasonic-ac-models?style=flat-square)](https://github.com/selvakk2k/panasonic-ac-models/releases)
[![AI-Assisted](https://img.shields.io/badge/AI%20Assisted-Antigravity%20%7C%20Claude-blueviolet?style=flat-square&logo=google)](https://github.com/selvakk2k)
[![AI Attribution](https://img.shields.io/badge/AI%20Attribution-AIA%20PAI%20Nc%20Hin-orange?style=flat-square)](https://aiattribution.github.io/interpret-attribution)

> [!NOTE]
> **Regional Scope**: This database specifically tracks Panasonic Air Conditioner SKUs certified and sold in the **Indian Market** (MirAIe IoT platform & BEE rating taxonomy). International Panasonic models (e.g. European/Australian units on *Panasonic Comfort Cloud*) use different SKU naming conventions and cloud APIs.

A comprehensive model capability database, lookup engine, and hardware-verified Infrared (IR) protocol generator for Panasonic Air Conditioners (Indian Market). Covers both **Wi-Fi / MirAIe smart models** and **IR remote-only models**, providing hardware feature flags for HVAC integrations, Home Assistant custom integrations, companion libraries, and dashboard cards.

---

## Table of Contents

1. [Installation](#installation)
2. [Model Capability Database & Lookup Engine](#model-capability-database--lookup-engine)
   - [Python Backend Usage](#python-backend-usage)
   - [JavaScript / Frontend CDN Usage](#javascript--frontend-cdn-usage)
   - [Hardware Feature Gating Rules](#hardware-feature-gating-rules)
3. [Infrared (IR) Protocol Engine](#infrared-ir-protocol-engine)
   - [Python IR Code Generation](#python-ir-code-generation)
   - [Parameters & Defaults](#generate_ir_code-parameters--defaults)
   - [Supported Output Formats & Target Hardware](#supported-output-formats--target-hardware)
4. [Database Summary](#database-summary)
5. [My Python Libraries](#my-python-libraries)
6. [Contributing & Authors](#contributing--authors)

---

## Installation

Install the Python package via `pip`:

```bash
pip install panasonic-ac-models
```

Or fetch the standalone JSON database directly in frontend cards via jsDelivr CDN:

```text
https://cdn.jsdelivr.net/gh/selvakk2k/panasonic-ac-models@main/models.json
```

---

## Model Capability Database & Lookup Engine

### Python Backend Usage

Query feature gating flags using the normalized lookup engine:

```python
from panasonic_ac_models import ACModelLookup

lookup = ACModelLookup()

# Query capability dictionary for any indoor SKU.
# Handles CS-CU-, CS/CU-, CU-, lowercase, and whitespace variants automatically.
caps = lookup.get_capabilities("CS-CU-EU18CKY5XFM")

print(f"Model Series: {caps['series']} (Gen {caps['generation']})")
print(f"Family Key:   {caps['family_key']}")
print(f"Resolved Via: {caps['resolved_via']}")
# - "database":     Exact match in models.json
# - "decoded":      Dynamically parsed via Indian BEE model syntax
# - "safe_default": Unrecognized SKU fallback (family_key="UNKNOWN", safe defaults applied)
# Note: Feature flags (has_wifi, has_heat_mode, has_nanoe) are returned as integer 1 or 0.

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
else:  # "none" -> Pre-2023 auto-convertible or fixed-speed: hide converti presets
    converti_presets = []
```

### JavaScript / Frontend CDN Usage

Fetch `models.json` directly from CDN in custom cards:

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

### Hardware Feature Gating Rules

| Feature | Applies To | Series / Condition |
|---|---|---|
| **Wi-Fi / MirAIe Smart** | Inverter splits & smart window ACs | NU, SU (W/WD/WF variants), EU, AU, HU, XU, EZ, KZ, WU, QU, YU, TU, VU, ZU, LU, KU, LN (inverter), XU (window), PU (commercial smart), PB (commercial tower) |
| **IR Remote Only** | Fixed-speed & non-smart models | KN (fixed-speed splits), XN (fixed-speed window ACs), LN-C (fixed-speed window ACs), RU (all generations: RU-A/B/C), SU titanium panel variants (T/TD/TF/TK suffix), PD, PU-5 (older commercial) |
| **Heat Mode** | Dual heat pump series | EZ and KZ series only |
| **Nanoe Ionizer** | Air purification premium series | HU and XU series only |
| **Nanoe-X (Commercial)** | Commercial heat pump cassettes | PU Gen 6/7/8, PB commercial tower |
| **Converti 8-in-1** | 2026+ generation models | NU/SU/WU/QU (Gen ≥ B) and EZ/HU/EU/AU (Gen ≥ C) |
| **Converti 7-in-1** | 2023–2025 generation models | All other 2023–2025 inverter splits |
| **No Converti** | Pre-2023 or fixed-speed / commercial | Gen W, X (sensor auto-scaling), fixed-speed models, all commercial cassettes |

---

## Infrared (IR) Protocol Engine

> [!TIP]
> **Production Reference Implementation**:
> For a complete, production-tested Home Assistant custom integration implementing this IR protocol engine alongside Wi-Fi and MQTT cloud/local control, see **[ha-miraie-ac-in](https://github.com/selvakk2k/ha-miraie-ac-in)**.

`panasonic-ac-models` includes a hardware-verified IR bitstream generator for Panasonic's Indian AC models. It supports full 27-byte state packets, 16-byte short frames (Display, Coil Clean, Powerful), and dual-vane / single-vane mirroring logic.

### Python IR Code Generation

```python
from panasonic_ac_models import generate_ir_code

# =============================================================
# 1. Standard Cooling with Dual-Vane Control (27-Byte Full Frame)
# =============================================================
ir_cool = generate_ir_code(
    mode="cool",           # "cool", "dry", "fan_only", "auto", "heat", "off"
    target_temp=24,        # 16 to 30°C
    fan="auto",            # "quiet", "low", "mid", "high", "auto"
    v_vane="V1",           # "V0" (Auto Swing), "V1" (Top) to "V5" (Bottom)
    h_vane="H0",           # "H0" (Auto Swing), "H1" (Left) to "H5" (Right), or None (Single-Vane)
    eco=False,
    nanoe=False,
    series="EU"            # Series profile (e.g. EU, NU, SU, HU, KZ, CS)
)

print(ir_cool["description"])
# => "EU Series | COOL 24°C (Fan: auto, V-Vane: V1, H-Vane: H0 [Dual-Vane], ECO: OFF, NANOE: OFF)"

# =============================================================
# 2. Eco Mode (Energy Saver)
# Clamps Byte 14 to 26°C and sets the physical Eco flag (Byte 22 = 0x08)
# =============================================================
ir_eco = generate_ir_code(
    mode="cool",
    target_temp=24,        # Clamped to 26°C in bitstream when eco=True
    fan="auto",
    v_vane="V1",
    eco=True
)

print(ir_eco["description"])
# => "EU Series | COOL 26°C (Fan: auto, V-Vane: V1, H-Vane: Mirrored [Single-Vane], ECO: ON, NANOE: OFF)"

# =============================================================
# 3. Dual Heat Pump (Heat Mode for EZ & KZ Series)
# =============================================================
ir_heat = generate_ir_code(
    mode="heat",
    target_temp=28,
    fan="high",
    v_vane="V5",           # Point louvers downward for heating
    series="KZ"
)

print(ir_heat["description"])
# => "KZ Hot & Cold Series | HEAT 28°C (Fan: high, V-Vane: V5, H-Vane: Mirrored [Single-Vane], ECO: OFF, NANOE: OFF)"

# =============================================================
# 4. Special 16-Byte Short-Frame Commands
# Instant single-action pulses that do not resend full temperature/fan state
# =============================================================

# Powerful / Turbo Boost:
ir_powerful = generate_ir_code(mode="powerful")
print(ir_powerful["description"])
# => "SPECIAL FEATURE: POWERFUL / TURBO"

# Toggle Indoor Unit Display LED / Temperature Screen:
ir_display = generate_ir_code(mode="display")
print(ir_display["description"])
# => "SPECIAL FEATURE: DISPLAY LED TOGGLE"

# Trigger Self-Clean / Coil Cleaning Cycle:
ir_clean = generate_ir_code(mode="clean")
print(ir_clean["description"])
# => "SPECIAL FEATURE: SELF CLEAN"

# Set Converti Capacity Preset (e.g. 80% or 110% High Capacity):
ir_conv80 = generate_ir_code(mode="converti_80")
print(ir_conv80["description"])
# => "CONVERTI MODE: 80% CAPACITY"

ir_conv110 = generate_ir_code(mode="converti_110")
print(ir_conv110["description"])
# => "CONVERTI MODE: 110% HIGH CAPACITY"

# Turn Off the AC:
ir_off = generate_ir_code(mode="off")
print(ir_off["description"])
# => "EU Series | OFF 24°C (Fan: low, V-Vane: V1, H-Vane: Mirrored [Single-Vane], ECO: OFF, NANOE: OFF)"

# =============================================================
# 5. Extracting Protocol Payloads for Target Hardware
# =============================================================

# Home Assistant Native 'infrared' Platform & ESPHome (List of microsecond timings):
raw_pulses = ir_cool["raw"]             # [3443, -1748, 434, -437, 469, -1311, ...]

# Broadlink RM4 / RM3 Hubs (Base64 string):
broadlink_code = ir_cool["broadlink_b64"]  # "JgBIAAGn..."

# Tuya Local Hubs (DP 201 Base64 string):
tuya_code = ir_cool["tuya_b64"]         # "B/4Dbg..."

# Tasmota MQTT (JSON string for cmnd/<device>/IRsend):
tasmota_payload = ir_cool["tasmota_json"] # '{"Protocol":"PANASONIC_AC","Bits":216,"Data":"0x..."}'

# Panasonic 54-char AEHA Hardware Hex Stream (ahea_hex kept as alias):
aeha_hex = ir_cool["aeha_hex"]           # "0x0220E004000000060220E004..."

# =============================================================
# 6. Hardware Dispatch Examples (Sending to Hardware)
# =============================================================

# --- Option A: Home Assistant Native 'infrared' Platform (ESPHome) ---
# from homeassistant.components.infrared import async_send_command, InfraredCommand
# await async_send_command(hass, "infrared.living_room_blaster", InfraredCommand(raw_pulses))

# --- Option B: Home Assistant 'remote' Service (Broadlink / Tuya) ---
# await hass.services.async_call("remote", "send_command", {
#     "entity_id": "remote.living_room_blaster",
#     "command": [f"b64:{broadlink_code}"]  # Or [tuya_code] for Tuya Local
# })

# --- Option C: Direct Python Broadlink SDK ---
# import base64, broadlink
# bl_device = broadlink.hello("192.168.1.50")
# bl_device.auth()
# bl_device.send_data(base64.b64decode(broadlink_code))

# --- Option D: MQTT / Tasmota (paho-mqtt) ---
# import paho.mqtt.publish as publish
# publish.single("cmnd/tasmota_ir/IRsend", tasmota_payload, hostname="192.168.1.10")
```

### `generate_ir_code()` Parameters & Defaults

| Argument | Type | Default | Description |
|:---|:---|:---:|:---|
| `mode` | `str` | `"cool"` | HVAC mode (`"cool"`, `"dry"`, `"fan_only"`, `"auto"`, `"heat"`, `"off"`) or short frame (`"display"`, `"clean"`, `"powerful"`, `"converti_80"`, etc.) |
| `target_temp` | `int` | `24` | Target temperature (16–30°C). Automatically clamped to 26°C when `eco=True`. |
| `fan` | `str` | `"low"` | Fan speed: `"quiet"`, `"low"`, `"mid"`, `"high"`, `"auto"` |
| `v_vane` | `str` | `"V1"` | Vertical louver: `"V0"` (Auto Swing), `"V1"` (Top) to `"V5"` (Bottom) |
| `h_vane` | `str` / `None` | `None` | Horizontal louver: `"H0"` (Auto Swing), `"H1"` to `"H5"`. When `None`, mirrors `v_vane` (Single-Vane). |
| `eco` | `bool` | `False` | Sets Byte 22 = `0x08` and clamps Byte 14 setpoint to 26°C. |
| `nanoe` | `bool` | `False` | Activates Nanoe-X air purification ionizer. |
| `series` | `str` | `"EU"` | Model series profile: `"EU"`, `"NU"`, `"SU"`, `"HU"`, `"KZ"`, `"CS"` |

> [!NOTE]
> **Short-Frame Precedence**: When using special short-frame commands (`mode="display"`, `"clean"`, `"powerful"`, `"converti_XX"`), state parameters (`target_temp`, `fan`, `v_vane`) are ignored since 16-byte pulses are dedicated single-action triggers.

---

### Supported Output Formats & Target Hardware

| Format Key | Output Type | Target Hardware / Platform | Verification Status |
|:---|:---|:---|:---|
| **`raw`** | `list[int]` | **Home Assistant Native `infrared` Platform** & **ESPHome** (`remote_receiver` / `remote_transmitter`) | ✅ **Hardware-Tested & Confirmed** (Tested and verified on physical AC hardware) |
| **`aeha_hex`** | `str` (Hex) | **Panasonic 54-char AEHA Hex Stream** (`0x0220E004...`) | ✅ **Hardware-Capture Verified** (Matches physical remote captures 1:1; `ahea_hex` alias retained) |
| **`tasmota_json`**| `str` (JSON) | **Tasmota MQTT** (`IRsend {"Protocol":"PANASONIC_AC","Bits":216,"Data":"..."}`) | ⚡ **Format Verified** *(Not tested on physical Tasmota hardware)* |
| **`broadlink_b64`**| `str` (Base64) | **Broadlink Hubs** (`RM4 Mini`, `RM4 Pro`, `RM3 Mini` via `remote.send_command`) | ⚡ **Format Verified** *(Not tested on physical Broadlink hardware)* |
| **`tuya_b64`** | `str` (Base64) | **Tuya Local / LocalTuya IR Hubs** (DP 201 via `remote.send_command`) | ⚡ **Format Verified** *(Not tested on physical Tuya hardware)* |
| **`pronto_hex`** | `str` (Hex) | **Pronto Hex (4-digit word sequence)** | ⚠️ **Experimental** *(Not tested on physical hardware; not recommended due to 2,200+ char buffer limits)* |

> [!WARNING]
> **Pronto Hex Limitation for AC Units**:
> Panasonic AC remotes transmit 216 bits (436 pulses), generating a Pronto string of over 2,200 characters. Many Home Assistant integrations (such as *HAIR* or low-buffer serial bridges) cannot parse Pronto strings of this length and may experience timing drift or buffer truncation. For production setups, use **Native `infrared` (`raw`)**, **Broadlink**, or **Tuya Base64**.

---

## Database Summary

- **Models Tracked**: 486 models across 144 hardware families.
  - **398 Wi-Fi / MirAIe Smart models** across 115 families — for cloud/MQTT integrations.
  - **88 IR Remote-Only models** across 29 families — for IR blaster integrations.
- **Data Sources**: Bureau of Energy Efficiency (BEE) certified labels, Panasonic India catalogs, empirical MirAIe telemetry, and live retail verification.

---

## My Python Libraries

| Library | PyPI Package | Description | Status |
| :--- | :--- | :--- | :--- |
| [Panasonic AC Models](https://github.com/selvakk2k/panasonic-ac-models) | `panasonic-ac-models` | Hardware profiles, capability lookup & IR protocol generator for Indian Panasonic ACs | `Stable` |
| [IFB Washer Models](https://github.com/selvakk2k/ifb-washer-models) | `ifb-washer-models` | Unified hardware database, model lookup & cycle capability gating for IFB smart washers | `Stable` |
| [MirAIe AC API Client](https://github.com/selvakk2k/miraie-ac-in) | `miraie-ac-in` | Async MQTT & REST API client for Panasonic MirAIe-connected Air Conditioners | `Stable` |

---

## Contributing & Authors

Pull requests are welcome! To add or correct a model:

1. Edit `models.json`.
2. Add the indoor SKU to the appropriate `indoor_units` array under `families`.
3. Set `has_wifi: 0` for IR-only models, `has_wifi: 1` for Wi-Fi smart models.
4. Submit a PR. Continuous Integration (`check-jsonschema`) will validate changes against `schema.json`.

### Authors & Credits
* **Lead Architecture & Hardware Validation**: [@selvakk2k](https://github.com/selvakk2k) — BEE catalog cross-referencing, empirical MirAIe telemetry, physical remote captures, and schema architecture.
* **Code Implementation & Engineering**: **Antigravity** (Google DeepMind) — lookup engine algorithms, 216-bit IR generator, format encoders (Broadlink, Pronto, Tuya, Native), and JSON validation suite.
* **Pre-Release Code Review & Auditing**: **Claude** (Anthropic) — independent schema verification, JSON structure audits, and edge-case testing.

Licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
