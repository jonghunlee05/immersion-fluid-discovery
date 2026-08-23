# IFD-003: Expand ThermoML Property Coverage and Ingestion Auditing

## Purpose

Expand the real-data validation introduced by IFD-002 from one viscosity source
to multiple priority properties while keeping the model-ready input restricted
to pure-liquid experimental measurements.

## Scope

- Add immutable NIST ThermoML samples covering density, isobaric heat capacity,
  and thermal conductivity.
- Register source URLs, DOIs, publication metadata, and SHA-256 hashes.
- Preserve the IFD-002 dynamic-viscosity source and behavior.
- Separate accepted pure-liquid target measurements from rejected records.
- Report mixtures, gas or ambiguous phases, unsupported properties, and missing
  property values with source context.
- Generate updated coverage, overlap, and rejection reports.
- Add regression tests against all real sample files.

## Commands

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Outputs

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
reports/data_audit/rejection_report.csv
```

Generated CSV outputs are ignored by Git because they are reproducible from the
immutable raw XML files and version-controlled code.

## Acceptance Criteria

- At least three target-property types beyond viscosity are parsed from real
  ThermoML sources.
- Raw XML files are stored unchanged and have registered SHA-256 hashes.
- Accepted output contains only single-component liquid records.
- Every accepted measurement retains a DOI and phase.
- Mixture sections and non-liquid measurements are excluded with explicit audit
  reasons.
- Coverage and overlap reports are reproducible.
- The existing IFD-002 viscosity result remains unchanged.
- Tests pass.

## Non-Goals

- Molecular identity resolution or RDKit processing.
- Descriptor generation or cross-source chemical deduplication.
- Classical ML, GNN, or generative-model training.
- Environmental filtering or final engineering thresholds.
