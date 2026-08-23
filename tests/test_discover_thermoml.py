import unittest

from immersion_ml.data.discover_thermoml import candidate_from_content


class ThermoMLDiscoveryTests(unittest.TestCase):
    def test_candidate_requires_pure_target_data(self):
        content = {
            "Citation": {
                "sDOI": "10.1234/example",
                "sTitle": "Example density source",
                "yrPubYr": "2025",
            },
            "Compound": [
                {"sCommonName": ["example liquid"]},
                {"sCommonName": ["reference liquid"]},
            ],
            "data_summary": {
                "pure": {
                    "VolumetricProp": {
                        "Mass density, kg/m3": {"data_points": 42, "data_sets": 2}
                    }
                },
                "binary": {
                    "VolumetricProp": {
                        "Mass density, kg/m3": {"data_points": 100, "data_sets": 4}
                    }
                },
            },
        }

        candidate = candidate_from_content(content, "density")

        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["pure_target_data_points"], 42)
        self.assertEqual(candidate["compound_count"], 2)
        self.assertEqual(
            candidate["compound_names"], "example liquid|reference liquid"
        )
        self.assertIsNone(candidate_from_content(content, "thermal_conductivity"))


if __name__ == "__main__":
    unittest.main()
