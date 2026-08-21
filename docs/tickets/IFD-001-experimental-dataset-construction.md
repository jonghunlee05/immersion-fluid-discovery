# IFD-001: Experimental Dataset Construction

## Purpose

Create the first reusable project scaffold for the experimental dataset
construction stage defined in `PROJECT_SPEC.md`.

This work supports ThermoML-style ingestion, raw measurement schema preservation,
unit normalization helpers, and initial data coverage/overlap audit reports.

## Scope

- Add the project package scaffold under `src/immersion_ml/`.
- Add config placeholders for properties, units, and unresolved screening rules.
- Define the canonical raw measurement schema with one experimental measurement
  per row.
- Add conservative ThermoML-style XML parsing for local files in `data/raw/`.
- Preserve source, identity, unit, temperature, pressure, phase, method, and
  uncertainty fields where available.
- Add coverage and overlap report utilities.
- Add standard-library tests for schema, unit conversion, audit behavior, and
  basic XML parsing.

## Commands

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Build the current dataset/audit outputs from local raw XML files:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
```

## Outputs

When raw ThermoML XML files are present, the build command writes:

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
```

Generated outputs are ignored by Git because they should be reproducible from
raw data and code.

## Non-Goals

- Do not fetch external ThermoML data automatically.
- Do not train classical ML, GNN, or generative models.
- Do not implement candidate screening, Pareto ranking, or MD/NEMD workflows.
- Do not hard-code unresolved environmental decisions such as fluorine-free vs
  non-PFAS.
- Do not invent final property thresholds.

## Validation

Current local validation:

```text
Ran 9 tests
OK
```

