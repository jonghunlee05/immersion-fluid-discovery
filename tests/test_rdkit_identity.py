import unittest

from immersion_ml.chemistry.rdkit_validation import (
    StructureValidationError,
    validate_structure,
)
from immersion_ml.data.identity import resolve_measurement_identities
from immersion_ml.data.schema import empty_raw_row
from immersion_ml.data.thermoml import parse_thermoml_directory_with_audit


ETHANOL_INCHI = "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"
ETHANOL_INCHIKEY = "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"


class RDKitIdentityTests(unittest.TestCase):
    def test_validate_structure_derives_identity_and_descriptors(self):
        structure = validate_structure(inchi=ETHANOL_INCHI)

        self.assertEqual(structure.inchikey, ETHANOL_INCHIKEY)
        self.assertEqual(structure.canonical_smiles, "CCO")
        self.assertEqual(structure.molecular_formula, "C2H6O")
        self.assertAlmostEqual(structure.molecular_weight, 46.069, places=3)
        self.assertEqual(structure.atom_count, 9)
        self.assertEqual(structure.heavy_atom_count, 3)
        self.assertEqual(structure.heteroatom_count, 1)
        self.assertEqual(structure.fluorine_count, 0)
        self.assertEqual(structure.formal_charge, 0)

    def test_missing_structure_is_rejected_explicitly(self):
        with self.assertRaisesRegex(
            StructureValidationError, "missing_structure_identifier"
        ):
            validate_structure()

    def test_smiles_canonicalization_is_stable_and_fluorine_is_counted(self):
        ethanol = validate_structure(smiles="OCC")
        fluorinated = validate_structure(smiles="FC(F)(F)")

        self.assertEqual(ethanol.canonical_smiles, "CCO")
        self.assertEqual(ethanol.inchikey, ETHANOL_INCHIKEY)
        self.assertEqual(fluorinated.fluorine_count, 3)

    def test_measurements_are_preserved_and_aliases_share_catalog_identity(self):
        rows = [
            _measurement("r1", "ethanol", "source-compound-1"),
            _measurement("r2", "ethyl alcohol", "source-compound-7"),
        ]

        resolved, catalog, report, issues = resolve_measurement_identities(rows)

        self.assertEqual([row["record_id"] for row in resolved], ["r1", "r2"])
        for source_row, resolved_row in zip(rows, resolved):
            for field, value in source_row.items():
                if field not in {"molecule_id", "canonical_SMILES"}:
                    self.assertEqual(resolved_row[field], value)
        self.assertEqual(
            [row["source_molecule_id"] for row in resolved],
            ["source-compound-1", "source-compound-7"],
        )
        self.assertTrue(all(row["molecule_id"] == ETHANOL_INCHIKEY for row in resolved))
        self.assertTrue(all(row["identity_status"] == "resolved" for row in resolved))
        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0]["source_names"], "ethanol|ethyl alcohol")
        self.assertEqual(catalog[0]["measurement_count"], 2)
        self.assertEqual(report[0]["measurement_count"], 2)
        self.assertEqual(issues, [])

    def test_conflicting_inchikey_is_audited_without_dropping_measurement(self):
        row = _measurement("r1", "ethanol", "source-compound-1")
        row["InChIKey"] = "AAAAAAAAAAAAAA-BBBBBBBBBB-C"

        resolved, catalog, _, issues = resolve_measurement_identities([row])

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["identity_status"], "conflict")
        self.assertEqual(resolved[0]["molecule_id"], "")
        self.assertEqual(resolved[0]["source_molecule_id"], "source-compound-1")
        self.assertEqual(catalog, [])
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["derived_InChIKey"], ETHANOL_INCHIKEY)

    def test_invalid_structure_is_retained_as_unresolved(self):
        row = _measurement("r1", "invalid", "source-compound-1")
        row["InChI"] = "not-an-inchi"

        resolved, catalog, _, issues = resolve_measurement_identities([row])

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["identity_status"], "unresolved")
        self.assertEqual(resolved[0]["property_value"], 789.0)
        self.assertEqual(catalog, [])
        self.assertEqual(issues[0]["issue"], "rdkit_parse_failed")

    def test_current_thermoml_corpus_resolves_without_dropping_rows(self):
        rows, _ = parse_thermoml_directory_with_audit("data/raw/thermoml")

        resolved, catalog, _, issues = resolve_measurement_identities(rows)

        self.assertEqual(len(resolved), 4637)
        self.assertEqual(len(catalog), 135)
        self.assertEqual(issues, [])
        self.assertEqual(
            sum(row["stereochemistry_status"] == "unspecified" for row in catalog),
            8,
        )
        self.assertEqual(sum(row["fluorine_count"] > 0 for row in catalog), 1)


def _measurement(record_id: str, name: str, source_molecule_id: str):
    row = empty_raw_row(record_id)
    row.update(
        {
            "molecule_id": source_molecule_id,
            "molecule_name": name,
            "InChI": ETHANOL_INCHI,
            "InChIKey": ETHANOL_INCHIKEY,
            "property_name": "density",
            "property_value": 789.0,
            "property_unit": "kg/m^3",
            "temperature_K": 298.15,
            "phase": "Liquid",
            "source_DOI": "10.1234/example",
            "source_record_id": record_id,
        }
    )
    return row


if __name__ == "__main__":
    unittest.main()
