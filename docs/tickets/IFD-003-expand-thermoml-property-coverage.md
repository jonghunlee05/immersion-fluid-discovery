# IFD-003: Expand ThermoML Property Coverage and Ingestion Auditing

## Purpose

Expand the real-data validation introduced by IFD-002 from one viscosity source
to a checksum-verified multi-source corpus spanning every current ThermoML
ingestion target while keeping model-ready input restricted to pure-liquid
experimental measurements.

## Scope

- Add immutable NIST ThermoML sources covering density, viscosity, isobaric heat
  capacity, thermal conductivity, vapor pressure, boiling temperature, and
  relative permittivity.
- Register source URLs, DOIs, publication metadata, and SHA-256 hashes.
- Provide a safe acquisition command that downloads missing registered sources,
  never overwrites raw files, and verifies every checksum.
- Discover pure-property candidates through the official ThermoML API and mark
  sources already present in the registry without automatically admitting data.
- Manually review discovery candidates for experimental method, relevant
  compounds, useful conditions, and complementary property overlap before
  registering their immutable XML.
- Audit other authoritative databases and define source-specific rules before
  combining their records with experimental ThermoML measurements.
- Preserve the IFD-002 dynamic-viscosity source and behavior.
- Separate accepted pure-liquid target measurements from rejected records.
- Report mixtures, gas or ambiguous phases, unsupported properties, and missing
  property values with source context.
- Generate updated coverage, overlap, and rejection reports.
- Flag exact repeated measurement conditions by within-source or cross-source
  scope without deleting or averaging any raw measurement.
- Add regression tests against all real sample files.

## Commands

```bash
PYTHONPATH=src python3 -m immersion_ml.data.download
PYTHONPATH=src python3 -m immersion_ml.data.download --download-missing
PYTHONPATH=src python3 -m immersion_ml.data.discover_thermoml --page-size 50
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Outputs

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
reports/data_audit/duplicate_report.csv
reports/data_audit/rejection_report.csv
```

Generated CSV outputs are ignored by Git because they are reproducible from the
immutable raw XML files and version-controlled code.

## Acceptance Criteria

- All seven current ThermoML ingestion targets are parsed from real sources.
- At least twenty-six independently registered ThermoML files contribute to the
  validation corpus.
- Raw XML files are stored unchanged and have registered SHA-256 hashes.
- Missing registered files can be restored reproducibly without overwriting
  existing raw data.
- Candidate discovery produces a review queue rather than silently downloading
  or accepting search results.
- Accepted output contains only single-component liquid records.
- Every accepted measurement retains a DOI and phase.
- Mixture sections and non-liquid measurements are excluded with explicit audit
  reasons.
- Coverage and overlap reports are reproducible.
- At least one molecule has measurements for all four core properties: thermal
  conductivity, dynamic viscosity, density, and isobaric heat capacity.
- Exact-condition duplicates are reported; none are silently removed or
  averaged.
- The existing IFD-002 viscosity result remains unchanged.
- Tests pass.

## Non-Goals

- Molecular identity resolution or RDKit processing.
- Descriptor generation or cross-source chemical deduplication.
- Classical ML, GNN, or generative-model training.
- Environmental filtering or final engineering thresholds.
