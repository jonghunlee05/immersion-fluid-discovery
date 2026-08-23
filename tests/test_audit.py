import unittest

from immersion_ml.data.audit import coverage_report, duplicate_report, overlap_report


class AuditTests(unittest.TestCase):
    def test_coverage_report_does_not_average_repeated_measurements(self):
        rows = [
            {
                "molecule_name": "A",
                "property_name": "density",
                "temperature_K": 298.15,
                "pressure_Pa": 101325.0,
                "source_type": "ThermoML",
            },
            {
                "molecule_name": "A",
                "property_name": "density",
                "temperature_K": 308.15,
                "pressure_Pa": 101325.0,
                "source_type": "ThermoML",
            },
        ]

        report = coverage_report(rows)

        self.assertEqual(report[0]["measurement_count"], 2)
        self.assertEqual(report[0]["unique_molecule_count"], 1)
        self.assertEqual(report[0]["temperature_min_K"], 298.15)
        self.assertEqual(report[0]["temperature_max_K"], 308.15)

    def test_overlap_report_counts_shared_molecules(self):
        rows = [
            {"molecule_name": "A", "property_name": "density"},
            {"molecule_name": "A", "property_name": "dynamic_viscosity"},
            {"molecule_name": "B", "property_name": "density"},
        ]

        report = overlap_report(rows)
        pair = next(
            row
            for row in report
            if row["property_set"] == "density|dynamic_viscosity"
        )

        self.assertEqual(pair["unique_molecule_count"], 1)

    def test_duplicate_report_flags_scope_without_dropping_rows(self):
        base = {
            "molecule_name": "A",
            "property_name": "density",
            "property_value": 800.0,
            "property_unit": "kg/m3",
            "temperature_K": 298.15,
            "pressure_Pa": 101325.0,
            "phase": "Liquid",
        }
        rows = [
            {**base, "source_DOI": "10.1/a", "source_record_id": "row-1"},
            {**base, "source_DOI": "10.1/a", "source_record_id": "row-2"},
            {**base, "source_DOI": "10.1/b", "source_record_id": "row-3"},
            {**base, "property_value": 801.0, "source_DOI": "10.1/b"},
        ]

        report = duplicate_report(rows)

        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["duplicate_count"], 3)
        self.assertEqual(report[0]["duplicate_scope"], "cross_source")
        self.assertEqual(report[0]["source_DOIs"], "10.1/a|10.1/b")


if __name__ == "__main__":
    unittest.main()
