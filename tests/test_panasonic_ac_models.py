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
        self.assertTrue(ir["ahea_hex"].startswith("0x"))
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

    def test_ir_generation_short_frames(self):
        nanoe_ir = generate_ir_code(mode="nanoe")
        self.assertGreater(len(nanoe_ir["raw"]), 100)
        self.assertIn("NANOE", nanoe_ir["description"])

        eco_ir = generate_ir_code(mode="eco")
        self.assertIn("ECO", eco_ir["description"])

if __name__ == "__main__":
    unittest.main()
