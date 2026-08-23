# IFD-002: Ingest First ThermoML Sample Dataset

## Purpose

Validate the IFD-001 experimental dataset construction scaffold against real
ThermoML XML files.

The goal is to learn whether the current ingestion code extracts useful
pure-liquid experimental records from real source files while preserving
temperature, pressure, units, phase, identity, and provenance.

## Scope

- Add a small initial ThermoML sample set under `data/raw/`.
- Run the current dataset construction command.
- Generate the parsed raw-measurement table and audit reports.
- Inspect parsed rows for property names, molecule identity, temperature,
  pressure, phase, units, DOI/source, and quality flags.
- Document any fields that cannot be parsed from the sample files.
- Make small parser fixes only if real ThermoML structure requires them.

## Commands

Run the dataset construction workflow:

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Expected Outputs

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
```

## Acceptance Criteria

- At least one real ThermoML XML file is present in `data/raw/`.
- The dataset construction command runs without crashing.
- Parsed experimental measurement rows are written to
  `data/interim/thermoml_raw_measurements.csv`.
- Coverage and overlap reports are generated.
- Parser limitations or missing fields are documented.
- Tests pass after any parser changes.

## Non-Goals

- Do not train classical ML, GNN, or generative models.
- Do not implement candidate screening, Pareto ranking, or MD/NEMD workflows.
- Do not resolve open research decisions such as non-PFAS vs fluorine-free.
- Do not invent final property thresholds.
- Do not manually edit raw ThermoML source files after adding them.

