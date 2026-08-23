# Immersion Fluid Discovery

Physics-validated generative molecular design of sustainable dielectric liquids for
single-phase immersion cooling.

This repository is currently in the experimental dataset construction stage. See
`PROJECT_SPEC.md` for the source of truth on scope, stage gates, and operating
rules.

## Current workflow

Create a local environment and install the pinned project dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

IFD-003 expanded the real ThermoML validation set across density, dynamic
viscosity, isobaric heat capacity, thermal conductivity, vapor pressure,
boiling temperature, and relative permittivity.

Verify the immutable raw sources against the version-controlled registry:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.download
```

To restore registered files that are missing locally, use the explicit download
option. Existing raw files are never overwritten:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.download --download-missing
```

Discover additional pure-property source candidates through the official NIST
ThermoML API:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.discover_thermoml --page-size 500
```

This produces `reports/data_audit/thermoml_candidate_sources.csv`. Candidate
sources are not admitted automatically: each XML file must pass pure-liquid,
property, provenance, and checksum review before registry inclusion.

The current IFD-003 corpus contains 4,637 accepted measurements from 30 sources.
Five molecules have coverage for all four core properties.

Build the pure-liquid interim dataset and audit reports with:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
```

The command writes reproducible generated outputs:

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
reports/data_audit/duplicate_report.csv
reports/data_audit/rejection_report.csv
```

IFD-004 validates the source-provided molecular structures with RDKit, preserves
all measurement rows, and builds a deduplicated molecule catalog:

```bash
PYTHONPATH=src .venv/bin/python -m immersion_ml.data.build_identity_dataset
```

This writes additional reproducible outputs:

```text
data/interim/thermoml_identity_resolved.csv
data/interim/molecule_catalog.csv
reports/data_audit/identity_resolution_report.csv
reports/data_audit/identity_issues.csv
```

The current corpus resolves all 4,637 measurements into 135 RDKit-validated
molecules without dropping any measurement rows.

Run the tests with:

```bash
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
```
