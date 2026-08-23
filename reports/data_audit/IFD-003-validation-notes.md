# IFD-003 Validation Notes

## Sources

IFD-003 now uses eleven unmodified XML files downloaded from the official NIST
ThermoML archive. Their URLs and SHA-256 hashes are recorded in
`references/thermoml_source_registry.csv`. The first increment established the
multi-property pipeline; the second increment scaled source and property
coverage on the same ticket.

## Accepted pure-liquid measurements

| Property | Measurements | Unique molecules | Temperature range (K) |
| --- | ---: | ---: | ---: |
| boiling temperature | 20 | 10 | Not applicable as a measurement condition |
| density | 200 | 14 | 233.0655–363.1779 |
| dynamic viscosity | 426 | 3 | 303.1–598.5 |
| isobaric heat capacity | 197 | 8 | 253.5–355.09 |
| relative permittivity | 145 | 1 | 303.7–393.0 |
| thermal conductivity | 512 | 3 | 301.73–577.25 |
| vapor pressure | 74 | 3 | 233.0655–363.1779 |

The combined interim dataset contains 1,574 measurements. All accepted records
have a liquid phase and source DOI.

## Rejections

- 571 gas, supercritical, or otherwise non-liquid measurements are excluded
  from the pure-liquid interim dataset.
- 20 multicomponent ThermoML sections are excluded. Their `record_count` values
  preserve how many property values each rejected section contains.
- Rejections retain their source file, DOI, ThermoML record reference, reason,
  property label where available, and phase where available.

## Overlap result

- Density and dynamic viscosity overlap for one molecule.
- Density and isobaric heat capacity overlap for three molecules.
- Dynamic viscosity and isobaric heat capacity overlap for one molecule.
- Density and vapor pressure overlap for two molecules.
- Isobaric heat capacity and vapor pressure overlap for one molecule.
- No molecule currently has all four core properties.

## Duplicate audit

The exact-condition audit flags 22 repeated groups within individual source
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
