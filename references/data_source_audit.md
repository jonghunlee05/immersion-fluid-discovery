# Experimental Data Source Audit

This audit controls which external sources may contribute to the project and
how their records must be labelled. `PROJECT_SPEC.md` remains authoritative.

## Approved experimental training source

### NIST ThermoML Archive

- Status: approved for experimental ingestion.
- Role: primary source for temperature- and pressure-dependent thermophysical
  measurements with method, uncertainty, phase, identity, and literature
  provenance.
- Access: <https://trc.nist.gov/ThermoML/>
- Rule: retain only pure-liquid target measurements in the interim table;
  preserve rejected mixtures and non-liquid records in the audit report.

## Candidate sources requiring source-specific ingestion policy

### AIST Thermophysical Property Database

- Status: promising; do not merge into training data yet.
- Coverage: thermal conductivity, heat capacity, density, viscosity, vapor
  pressure, dielectric constant, and other properties for liquids and other
  material classes.
- Access: <https://tpds.db.aist.go.jp/opendata/data100806_en.html>
- Required checks: per-record experimental status, original citation,
  measurement conditions, units, reuse terms, and machine-readable access.

### EPA CompTox Chemicals Dashboard

- Status: approved for source discovery and future safety/flash-point audit;
  not yet approved as direct experimental training truth.
- Coverage: structures plus experimental and predicted physicochemical,
  toxicity, exposure, and hazard information.
- Access: <https://comptox.epa.gov/dashboard/>
- Required checks: select experimental records explicitly, retain the original
  contributor/reference, and never mix predicted summary values with measured
  values.

### NBS Circular 514 — Table of Dielectric Constants of Pure Liquids

- Status: authoritative critically evaluated compilation; parser and schema
  policy still required.
- Coverage: static dielectric constants for more than 800 pure liquids,
  including temperature relationships, accuracy indications, and bibliography.
- Access:
  <https://www.govinfo.gov/content/pkg/GOVPUB-C13-68b1154fcd941d0c6d982cb1dcd5b632/pdf/GOVPUB-C13-68b1154fcd941d0c6d982cb1dcd5b632.pdf>
- Rule: label values as critically evaluated compilation data, not direct raw
  experimental measurements; retain table accuracy and cited original sources.

### NIST Chemistry WebBook

- Status: approved for reference baselines, source discovery, and validation;
  not interchangeable with raw experimental ThermoML rows.
- Coverage: thermochemistry for thousands of compounds and recommended or
  correlated thermophysical data for a smaller fluid set.
- Access: <https://webbook.nist.gov/>
- Rule: distinguish individual literature measurements from generated,
  recommended, or correlation-derived tables.

### PubChem

- Status: approved for molecular identity and source discovery only at this
  stage.
- Access: <https://pubchem.ncbi.nlm.nih.gov/>
- Rule: PUG-View annotations must be traced to their original contributor or
  publication before a value can be considered for experimental training.

### OECD eChemPortal

- Status: approved as a gateway for later physicochemical, environmental, and
  hazard evidence discovery.
- Access: <https://www.echemportal.org/echemportal/>
- Rule: the participating database remains the data owner; retain the ultimate
  source and study-summary context rather than citing the portal as the
  experiment.

## Excluded from experimental ground truth

- Random web property tables.
- Unsourced aggregators.
- Values without temperature, phase, units, or provenance where those fields
  are scientifically required.
- Predicted database values unless explicitly labelled and stored outside the
  experimental training target.
- LLM-generated values.
