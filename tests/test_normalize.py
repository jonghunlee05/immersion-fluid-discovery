import unittest

from immersion_ml.data.normalize import (
    UnitConversionError,
    dynamic_viscosity_from_kinematic,
    normalize_pressure,
    normalize_property_value,
    normalize_temperature,
)


class NormalizeTests(unittest.TestCase):
    def test_temperature_conversion_to_kelvin(self):
        self.assertAlmostEqual(normalize_temperature(25.0, "C"), 298.15)
        self.assertAlmostEqual(normalize_temperature(298.15, "K"), 298.15)

    def test_pressure_conversion_to_pa(self):
        self.assertAlmostEqual(normalize_pressure(1.0, "kPa"), 1000.0)
        self.assertAlmostEqual(normalize_pressure(1.0, "bar"), 100000.0)

    def test_dynamic_and_kinematic_viscosity_are_distinct(self):
        nu = normalize_property_value("kinematic_viscosity", 2.0, "cSt")
        self.assertAlmostEqual(nu, 2e-6)
        self.assertAlmostEqual(dynamic_viscosity_from_kinematic(nu, 800.0), 0.0016)

    def test_unsupported_unit_fails_clearly(self):
        with self.assertRaises(UnitConversionError):
            normalize_property_value("density", 1.0, "banana")


if __name__ == "__main__":
    unittest.main()
