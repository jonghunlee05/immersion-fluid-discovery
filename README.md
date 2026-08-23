# Immersion Fluid Discovery

Physics-validated generative molecular design of sustainable dielectric liquids for
single-phase immersion cooling.

This repository is currently in the experimental dataset construction stage. See
`PROJECT_SPEC.md` for the source of truth on scope, stage gates, and operating
rules.

## Current workflow

IFD-003 expands the real ThermoML validation set across density, dynamic
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

Run the tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
