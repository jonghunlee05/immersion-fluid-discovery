import unittest

from immersion_ml.data.schema import RAW_MEASUREMENT_COLUMNS, RawMeasurement


class SchemaTests(unittest.TestCase):
    def test_raw_measurement_preserves_project_columns(self):
        row = RawMeasurement(
            record_id="r1",
            molecule_name="example",
            property_name="density",
            property_value=800.0,
            property_unit="kg/m^3",
            temperature_K=298.15,
            source_DOI="10.1234/example",
        ).to_row()

        self.assertEqual(list(row), list(RAW_MEASUREMENT_COLUMNS))
        self.assertEqual(row["source_DOI"], "10.1234/example")
        self.assertEqual(row["temperature_K"], 298.15)


if __name__ == "__main__":
    unittest.main()
