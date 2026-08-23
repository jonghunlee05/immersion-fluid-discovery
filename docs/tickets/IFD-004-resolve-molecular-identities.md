# IFD-004: Resolve Molecular Identities and Build the RDKit-Validated Catalog

## Purpose

Convert IFD-003's provenance-preserving experimental measurements into an
identity-resolved interim dataset and a deduplicated molecule catalog. Validate
source-provided structures with RDKit without averaging or deleting measurement
rows.

## Scope

- Read the reproducible IFD-003 interim measurement table.
- Preserve every raw-schema field and original source-local molecule identifier.
- Resolve structures from source-provided InChI, falling back to source-provided
  SMILES when available.
- Parse and sanitize structures with RDKit.
- Verify source InChIKeys against RDKit-derived InChIKeys.
- Assign the verified InChIKey as the stable resolved `molecule_id`.
- Generate canonical and isomeric SMILES and a deduplicated molecule catalog.
- Calculate molecular formula, molecular weight, logP, TPSA, atom counts, ring
  count, heteroatom count, fluorine count, formal charge, rotatable bonds, and
  fragment count.
- Record assigned and unassigned stereocenters without inventing stereochemistry.
- Retain unresolved or conflicting measurements and audit them explicitly.
- Keep fluorinated molecules until the environmental rule is finalized.

The current ThermoML corpus already supplies InChI and InChIKey for every
accepted measurement. No network identity lookup is required by this ticket.

## Commands

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
PYTHONPATH=src python3 -m immersion_ml.data.build_identity_dataset
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Outputs

```text
data/interim/thermoml_identity_resolved.csv
data/interim/molecule_catalog.csv
reports/data_audit/identity_resolution_report.csv
reports/data_audit/identity_issues.csv
```

Generated CSV outputs remain ignored by Git because they are reproducible from
the committed raw XML, registry, and code.

## Acceptance Criteria

- All 4,637 current accepted measurements appear in the resolved output.
- Every output measurement retains its original `record_id`, source provenance,
  conditions, value, unit, and source-local molecule identifier.
- The current corpus resolves to 135 deterministic RDKit-validated molecule
  identities without identifier conflicts.
- Resolved measurements use a verified InChIKey as their stable `molecule_id`.
- Duplicate aliases map to one catalog identity.
- Invalid, missing, or conflicting structures remain in the measurement output
  and appear in the identity-issues audit.
- Unspecified stereochemistry is represented explicitly.
- Fluorinated structures are retained and counted rather than filtered.
- Tests cover parsing, canonicalization, descriptor calculation, alias
  deduplication, conflict auditing, stereochemistry, and row preservation.
- All existing IFD-003 tests continue to pass.

## Non-Goals

- External identity enrichment when a source structure is missing.
- Property-value unit normalization or averaging.
- Outlier removal or scientific conflict resolution.
- Environmental, PFAS, or fluorine-free filtering.
- Final ML-target selection or train/test splitting.
- Classical ML, GNN, or generative-model training.
