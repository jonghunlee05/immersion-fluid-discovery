# IFD-003 Validation Notes

## Sources

IFD-003 now uses thirty unmodified XML files downloaded from the official NIST
ThermoML archive. Their URLs and SHA-256 hashes are recorded in
`references/thermoml_source_registry.csv`. The first increment established the
multi-property pipeline; subsequent increments scaled source and property
coverage on the same ticket. Sources were manually reviewed from the generated
discovery queue before admission. The latest four-source batch specifically
targeted missing properties for molecules already having three core properties.

## Accepted pure-liquid measurements

| Property | Measurements | Unique molecules | Temperature range (K) |
| --- | ---: | ---: | ---: |
| boiling temperature | 32 | 22 | Not applicable as a measurement condition |
| density | 794 | 30 | 233.0655–363.1779 |
| dynamic viscosity | 988 | 16 | 273.15–598.5 |
| isobaric heat capacity | 487 | 16 | 253.5–483.15 |
| relative permittivity | 255 | 17 | 278.15–393.0 |
| thermal conductivity | 1,685 | 65 | 245.46–577.25 |
| vapor pressure | 396 | 16 | 233.0655–453.15 |

The combined interim dataset contains 4,637 measurements. All accepted records
have a liquid phase and source DOI.

## Rejections

- 605 gas, supercritical, or otherwise non-liquid measurements are excluded
  from the pure-liquid interim dataset.
- 68 multicomponent ThermoML sections are excluded. Their `record_count` values
  preserve how many property values each rejected section contains.
- 1,080 unsupported-property records are retained in the rejection audit rather
  than entering target-property tables.
- Rejections retain their source file, DOI, ThermoML record reference, reason,
  property label where available, and phase where available.

## Overlap result

- Density and dynamic viscosity overlap for nine molecules.
- Density and isobaric heat capacity overlap for seven molecules.
- Dynamic viscosity and isobaric heat capacity overlap for six molecules.
- Density and relative permittivity overlap for nine molecules.
- Density and vapor pressure overlap for three molecules.
- Isobaric heat capacity and vapor pressure overlap for three molecules.
- Five molecules now have all four core properties: cyclohexane, dodecane,
  ethanol, hexane, and octane. This meets the overlap-first stopping target set
  for IFD-003.

## Duplicate audit

The exact-condition audit flags 56 repeated groups within individual source
files. It finds zero duplicate groups spanning different DOI sources. These rows
remain in the raw-measurement table as required; the report provides their
source-record identifiers for later scientific review.

The expanded corpus is sufficient to validate all current target-property
ingestion paths. It remains a curated validation corpus rather than a final
archive-scale coverage audit, and its per-property molecule counts are still too
small for model training.

## Parser correction

Property alias matching now checks exact and longer aliases before broad
substrings. This prevents `kinematic viscosity` from being incorrectly labeled
as `dynamic_viscosity` through the shorter `viscosity` alias.

ThermoML's combined `Vapor or sublimation pressure` label is accepted as vapor
pressure only when its property phase is liquid. Solid and non-liquid records
remain excluded by the phase audit.

## Discovery and external-source audit

The expanded ThermoML API discovery command generated 1,626 pure-property
source candidates with a page-size limit of 500 per configured target. Search
results remain a review queue; they are not downloaded or accepted
automatically.

`references/data_source_audit.md` records the current assessment of AIST TPDS,
EPA CompTox, NBS Circular 514, NIST Chemistry WebBook, PubChem, and OECD
eChemPortal. None of these sources is currently mixed into the ThermoML
experimental table without a source-specific ingestion and provenance policy.
