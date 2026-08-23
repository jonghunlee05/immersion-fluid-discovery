import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from immersion_ml.data.audit import duplicate_report
from immersion_ml.data.thermoml import (
    canonical_property_name,
    parse_thermoml_directory_with_audit,
    parse_thermoml_file,
    parse_thermoml_file_with_audit,
    write_raw_measurements_csv,
)


class ThermoMLTests(unittest.TestCase):
    def test_property_alias_mapping(self):
        self.assertEqual(canonical_property_name("Mass density"), "density")
        self.assertEqual(canonical_property_name("Dielectric constant"), "relative_permittivity")
        self.assertEqual(canonical_property_name("Kinematic viscosity, m2/s"), "kinematic_viscosity")
        self.assertIsNone(canonical_property_name("melting temperature"))

    def test_parse_thermoml_style_xml_preserves_provenance(self):
        with TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "sample.xml"
            xml_path.write_text(
                """<?xml version="1.0"?>
<ThermoML>
  <Citation>
    <Title>Example source title</Title>
    <DOI>10.1234/example</DOI>
    <Year>2024</Year>
  </Citation>
  <Compound id="c1">
    <Name>Example liquid</Name>
    <CAS>123-45-6</CAS>
    <SMILES>CCO</SMILES>
  </Compound>
  <PureOrMixtureData id="m1">
    <Property>Mass density</Property>
    <Value unit="kg/m^3">789.0</Value>
    <Temperature unit="K">298.15</Temperature>
    <Pressure unit="kPa">101.325</Pressure>
    <Phase>liquid</Phase>
    <Method>oscillating tube</Method>
  </PureOrMixtureData>
</ThermoML>
""",
                encoding="utf-8",
            )

            rows = parse_thermoml_file(xml_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["molecule_name"], "Example liquid")
            self.assertEqual(rows[0]["property_name"], "density")
            self.assertEqual(rows[0]["property_value"], 789.0)
            self.assertEqual(rows[0]["property_unit"], "kg/m^3")
            self.assertEqual(rows[0]["temperature_K"], 298.15)
            self.assertEqual(rows[0]["pressure_Pa"], 101325.0)
            self.assertEqual(rows[0]["source_DOI"], "10.1234/example")
            self.assertIsNone(rows[0]["quality_flag"])

            output_csv = Path(temp_dir) / "out.csv"
            write_raw_measurements_csv(rows, output_csv)
            self.assertTrue(output_csv.read_text(encoding="utf-8").startswith("record_id,"))

    def test_parse_real_thermoml_property_variable_structure(self):
        xml_path = Path("data/raw/thermoml/10.1021_acs.jced.5b00270.xml")
        if not xml_path.exists():
            self.skipTest("Real ThermoML sample file is not present.")

        rows = parse_thermoml_file(xml_path)

        self.assertEqual(len(rows), 94)
        self.assertEqual({row["property_name"] for row in rows}, {"dynamic_viscosity"})
        self.assertEqual({row["molecule_name"] for row in rows}, {"cyclohexane", "decane"})
        self.assertEqual({row["phase"] for row in rows}, {"Liquid"})
        self.assertEqual({row["property_unit"] for row in rows}, {"Pa*s"})
        self.assertTrue(all(row["temperature_K"] is not None for row in rows))
        self.assertTrue(all(row["pressure_Pa"] is not None for row in rows))
        self.assertTrue(all(row["source_DOI"] == "10.1021/acs.jced.5b00270" for row in rows))

    def test_audited_parse_excludes_gas_and_reports_rejection(self):
        with TemporaryDirectory() as temp_dir:
            xml_path = Path(temp_dir) / "sample.xml"
            xml_path.write_text(
                """<?xml version="1.0"?>
<ThermoML>
  <Citation><Title>Phase audit</Title><DOI>10.1234/phase</DOI></Citation>
  <Compound id="c1"><Name>Example fluid</Name></Compound>
  <PureOrMixtureData id="liquid">
    <Property>Mass density</Property><Value unit="kg/m^3">789</Value>
    <Temperature unit="K">298.15</Temperature><Phase>liquid</Phase>
  </PureOrMixtureData>
  <PureOrMixtureData id="gas">
    <Property>Mass density</Property><Value unit="kg/m^3">1.2</Value>
    <Temperature unit="K">350</Temperature><Phase>gas</Phase>
  </PureOrMixtureData>
</ThermoML>
""",
                encoding="utf-8",
            )

            rows, rejections = parse_thermoml_file_with_audit(xml_path)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["phase"], "liquid")
            self.assertEqual(len(rejections), 1)
            self.assertEqual(rejections[0]["reason"], "non_liquid_or_ambiguous_phase")

    def test_parse_ifd003_real_samples(self):
        expected = {
            "10.1016_j.tca.2005.08.012.xml": {"density": 18},
            "10.1016_j.jct.2012.07.018.xml": {
                "density": 121,
                "isobaric_heat_capacity": 35,
            },
            "10.1016_j.fluid.2018.07.011.xml": {"thermal_conductivity": 272},
        }
        expected_rejections = {
            "10.1016_j.tca.2005.08.012.xml": {
                "mixture_or_multicomponent_section": 14
            },
            "10.1016_j.jct.2012.07.018.xml": {
                "mixture_or_multicomponent_section": 6
            },
            "10.1016_j.fluid.2018.07.011.xml": {
                "non_liquid_or_ambiguous_phase": 305
            },
        }

        for filename, expected_counts in expected.items():
            with self.subTest(filename=filename):
                xml_path = Path("data/raw/thermoml") / filename
                if not xml_path.exists():
                    self.skipTest(f"Real ThermoML sample is missing: {filename}")
                rows, rejections = parse_thermoml_file_with_audit(xml_path)
                self.assertEqual(
                    Counter(row["property_name"] for row in rows), expected_counts
                )
                self.assertTrue(all(row["phase"] == "Liquid" for row in rows))
                self.assertTrue(all(row["source_DOI"] for row in rows))
                self.assertEqual(
                    Counter(row["reason"] for row in rejections),
                    expected_rejections[filename],
                )

    def test_scaled_ifd003_corpus_coverage(self):
        rows, rejections = parse_thermoml_directory_with_audit("data/raw/thermoml")

        self.assertEqual(
            Counter(row["property_name"] for row in rows),
            {
                "boiling_temperature": 20,
                "density": 200,
                "dynamic_viscosity": 426,
                "isobaric_heat_capacity": 197,
                "relative_permittivity": 145,
                "thermal_conductivity": 512,
                "vapor_pressure": 74,
            },
        )
        self.assertTrue(all(row["quality_flag"] is None for row in rows))
        self.assertTrue(all(row["source_DOI"] for row in rows))
        self.assertEqual(
            Counter(row["reason"] for row in rejections),
            {
                "mixture_or_multicomponent_section": 20,
                "non_liquid_or_ambiguous_phase": 571,
            },
        )
        duplicates = duplicate_report(rows)
        self.assertEqual(len(duplicates), 22)
        self.assertEqual(
            Counter(row["duplicate_scope"] for row in duplicates),
            {"within_source": 22},
        )


if __name__ == "__main__":
    unittest.main()
