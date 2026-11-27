import unittest

from panasonic_ac_models import ACModelLookup, get_bee_profile


class TestBeeProfile(unittest.TestCase):
    def test_exact_bee_match(self):
        prof = get_bee_profile("CS-CU-EU18CKY5XFM")
        self.assertEqual(prof["resolved_via"], "bee_database")
        self.assertEqual(prof["ton"], 1.45)
        self.assertEqual(prof["star_rating"], 5)
        self.assertEqual(prof["iseer"], 5.8)
        self.assertAlmostEqual(prof["rated_cooling_w"], 5099.4, delta=5.0)
        self.assertAlmostEqual(prof["rated_power_w"], 1477.7, delta=15.0)
        self.assertAlmostEqual(prof["half_power_w"], 480.4, delta=10.0)
        self.assertAlmostEqual(prof["min_power_w"], 288.2, delta=10.0)

    def test_fallback_derived_profile(self):
        lookup = ACModelLookup()
        prof = lookup.get_bee_profile("CS-UNKNOWN999")
        self.assertEqual(prof["resolved_via"], "default_derived")
        self.assertGreater(prof["rated_cooling_w"], 0)
        self.assertGreater(prof["rated_power_w"], prof["half_power_w"])
        self.assertGreater(prof["half_power_w"], prof["min_power_w"])


if __name__ == "__main__":
    unittest.main()

