import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from immersion_ml.data.thermoml import (
    canonical_property_name,
    parse_thermoml_file,
    write_raw_measurements_csv,
)


class ThermoMLTests(unittest.TestCase):
    def test_property_alias_mapping(self):
        self.assertEqual(canonical_property_name("Mass density"), "density")
        self.assertEqual(canonical_property_name("Dielectric constant"), "relative_permittivity")
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


if __name__ == "__main__":
    unittest.main()
