import unittest
from panasonic_ac_models import ACModelLookup, decode_model_string, generate_ir_code

class TestPanasonicACModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lookup = ACModelLookup()

    def test_su_tonnage_swing_type(self):
        # 1.0T and 1.5T SU units are 2-way swing
        su12 = self.lookup.get_capabilities("CS-SU12BKY3")
        self.assertEqual(su12["series"], "SU")
        self.assertEqual(su12["swing_type"], "2-way")

        # 2.0T+ SU units are 4-way swing
        su24 = self.lookup.get_capabilities("CS-SU24BKY3")
        self.assertEqual(su24["series"], "SU")
        self.assertEqual(su24["swing_type"], "4-way")

    def test_ru_non_wifi(self):
        # RU series (like CS-CU-RU18CKY-1) is non-wifi IR unit
        ru18 = self.lookup.get_capabilities("CS-CU-RU18CKY-1")
        self.assertEqual(ru18["series"], "RU")
        self.assertEqual(ru18["has_wifi"], 0)
        self.assertEqual(ru18["swing_type"], "2-way")

    def test_heat_and_nanoe(self):
        # EZ series has heat
        ez = self.lookup.get_capabilities("CS/CU-EZ12CKY")
        self.assertEqual(ez["has_heat_mode"], 1)

        # XU series has nanoe
        xu = self.lookup.get_capabilities("CS-XU18WKYF")
        self.assertEqual(xu["has_nanoe"], 1)

    def test_fixed_speed_2way_swing(self):
        kn = self.lookup.get_capabilities("CS-KN12AKY")
        self.assertEqual(kn["speed_type"], "fixed")
        self.assertEqual(kn["swing_type"], "2-way")
        self.assertEqual(kn["has_wifi"], 0)

    def test_ir_generation_cool_mode(self):
        ir = generate_ir_code(mode="cool", target_temp=24, fan="low", v_vane="V1", h_vane="H0", series="EU")
        self.assertIn("raw", ir)
        self.assertGreater(len(ir["raw"]), 100)
        self.assertTrue(ir["aeha_hex"].startswith("0x"))
        self.assertEqual(ir["aeha_hex"], ir["ahea_hex"])
        self.assertIn("tasmota_json", ir)
        self.assertIn("broadlink_b64", ir)
        self.assertIn("tuya_b64", ir)
        self.assertIn("pronto_hex", ir)

    def test_ir_generation_all_fan_speeds(self):
        # Hardware-verified fan modes against fancaptures.txt
        # Quiet
        quiet_ir = generate_ir_code(mode="cool", target_temp=26, fan="quiet", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(quiet_ir["ahea_hex"], "0x0220E004000000060220E00400393480A10D000EE0200089000038")

        # Off alias (backward compatibility)
        off_ir = generate_ir_code(mode="cool", target_temp=26, fan="off", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(off_ir["ahea_hex"], "0x0220E004000000060220E00400393480A10D000EE0200089000038")

        # Low
        low_ir = generate_ir_code(mode="cool", target_temp=26, fan="low", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(low_ir["ahea_hex"], "0x0220E004000000060220E00400393480310D000EE00000890000A8")

        # Medium
        med_ir = generate_ir_code(mode="cool", target_temp=26, fan="medium", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(med_ir["ahea_hex"], "0x0220E004000000060220E00400393480510D000EE00000890000C8")

        # High
        high_ir = generate_ir_code(mode="cool", target_temp=26, fan="high", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(high_ir["ahea_hex"], "0x0220E004000000060220E00400393480710D000EE00000890000E8")

        # Auto
        auto_ir = generate_ir_code(mode="cool", target_temp=26, fan="auto", v_vane="V1", h_vane="H0", series="EU")
        self.assertEqual(auto_ir["ahea_hex"], "0x0220E004000000060220E00400393480A10D000EE0000089000018")

    def test_ir_generation_eco_hardware_captures(self):
        # Hardware-verified against physical remote captures
        # ECO ON: forces 26C (0x34) and sets Byte 22 to 0x08
        eco_on = generate_ir_code(mode="cool", target_temp=24, fan="auto", v_vane="V1", h_vane="H0", eco=True, series="EU")
        self.assertEqual(eco_on["ahea_hex"], "0x0220E004000000060220E00400393480A10D000EE0000889000020")

        # ECO OFF: maintains requested temperature 27C (0x36) and clears Byte 22 to 0x00
        eco_off = generate_ir_code(mode="cool", target_temp=27, fan="auto", v_vane="V1", h_vane="H0", eco=False, series="EU")
        self.assertEqual(eco_off["ahea_hex"], "0x0220E004000000060220E00400393680A10D000EE000008900001A")

    def test_ir_generation_short_frames(self):
        nanoe_ir = generate_ir_code(mode="nanoe")
        self.assertGreater(len(nanoe_ir["raw"]), 100)
        self.assertIn("NANOE", nanoe_ir["description"])

        clean_ir = generate_ir_code(mode="clean")
        self.assertIn("CLEAN", clean_ir["description"])

    def test_decode_ir_code_full_frame_roundtrip(self):
        from panasonic_ac_models import decode_ir_code

        # Cool 24°C, Low Fan, V1, H2
        ir = generate_ir_code(mode="cool", target_temp=24, fan="low", v_vane="V1", h_vane="H2", series="EU")
        decoded = decode_ir_code(ir["aeha_hex"])
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["packet_type"], "full_frame")
        self.assertEqual(decoded["power"], "on")
        self.assertEqual(decoded["mode"], "cool")
        self.assertEqual(decoded["temperature"], 24)
        self.assertEqual(decoded["fan_speed"], "low")
        self.assertEqual(decoded["v_vane"], "V1")
        self.assertEqual(decoded["h_vane"], "H2")
        self.assertFalse(decoded["eco"])

        # Eco Mode ON
        eco_ir = generate_ir_code(mode="cool", target_temp=22, fan="auto", v_vane="V1", h_vane="H0", eco=True, series="EU")
        decoded_eco = decode_ir_code(eco_ir["aeha_hex"])
        self.assertIsNotNone(decoded_eco)
        self.assertEqual(decoded_eco["mode"], "cool")
        self.assertEqual(decoded_eco["temperature"], 26)
        self.assertTrue(decoded_eco["eco"])

        # Quiet Fan
        quiet_ir = generate_ir_code(mode="cool", target_temp=26, fan="quiet", v_vane="V1", h_vane="H0", series="EU")
        decoded_quiet = decode_ir_code(quiet_ir["aeha_hex"])
        self.assertIsNotNone(decoded_quiet)
        self.assertEqual(decoded_quiet["fan_speed"], "quiet")

        # Off Mode
        off_ir = generate_ir_code(mode="off", target_temp=24, fan="auto", v_vane="V1", h_vane="H0", series="EU")
        decoded_off = decode_ir_code(off_ir["aeha_hex"])
        self.assertIsNotNone(decoded_off)
        self.assertEqual(decoded_off["power"], "off")
        self.assertEqual(decoded_off["mode"], "off")

    def test_decode_ir_code_short_frames(self):
        from panasonic_ac_models import decode_ir_code

        # Powerful
        powerful_ir = generate_ir_code(mode="powerful")
        dec_pow = decode_ir_code(powerful_ir["aeha_hex"])
        self.assertIsNotNone(dec_pow)
        self.assertEqual(dec_pow["packet_type"], "short_frame")
        self.assertEqual(dec_pow["action"], "powerful")
        self.assertTrue(dec_pow["powerful"])

        # Display
        display_ir = generate_ir_code(mode="display")
        dec_disp = decode_ir_code(display_ir["aeha_hex"])
        self.assertIsNotNone(dec_disp)
        self.assertEqual(dec_disp["action"], "display")
        self.assertTrue(dec_disp["display"])

        # Clean
        clean_ir = generate_ir_code(mode="clean")
        dec_clean = decode_ir_code(clean_ir["aeha_hex"])
        self.assertIsNotNone(dec_clean)
        self.assertEqual(dec_clean["action"], "clean")
        self.assertTrue(dec_clean["clean"])

        # Converti 80%
        c80_ir = generate_ir_code(mode="converti_80")
        dec_c80 = decode_ir_code(c80_ir["aeha_hex"])
        self.assertIsNotNone(dec_c80)
        self.assertEqual(dec_c80["converti"], "cv_80")

    def test_decode_ir_code_multiple_input_types(self):
        from panasonic_ac_models import decode_ir_code

        ir = generate_ir_code(mode="cool", target_temp=25, fan="medium", v_vane="V3", h_vane="H3", series="EU")

        # 1. Raw Pulses
        dec_raw = decode_ir_code(ir["raw"])
        self.assertIsNotNone(dec_raw)
        self.assertEqual(dec_raw["temperature"], 25)
        self.assertEqual(dec_raw["fan_speed"], "medium")
        self.assertEqual(dec_raw["v_vane"], "V3")
        self.assertEqual(dec_raw["h_vane"], "H3")

        # 2. Tasmota JSON String
        dec_tasmota = decode_ir_code(ir["tasmota_json"])
        self.assertIsNotNone(dec_tasmota)
        self.assertEqual(dec_tasmota["temperature"], 25)

        # 3. Dict input
        dec_dict = decode_ir_code({"Protocol": "PANASONIC_AC", "Bits": 216, "Data": ir["aeha_hex"]})
        self.assertIsNotNone(dec_dict)
        self.assertEqual(dec_dict["temperature"], 25)

        # 4. Invalid Checksum / Corrupted input
        self.assertIsNone(decode_ir_code("0x0220E004000000060220E00400393480A10D000EE02000890000FF"))
        self.assertIsNone(decode_ir_code("invalid_payload"))
        self.assertIsNone(decode_ir_code([]))

if __name__ == "__main__":
    unittest.main()
