# IFD-003 Validation Notes

## Sources

IFD-003 adds three unmodified XML files downloaded from the official NIST
ThermoML archive. Their URLs and SHA-256 hashes are recorded in
`references/thermoml_source_registry.csv`.

## Accepted pure-liquid measurements

| Property | Measurements | Unique molecules | Temperature range (K) |
| --- | ---: | ---: | ---: |
| density | 139 | 11 | 273.15–333.15 |
| dynamic viscosity | 94 | 2 | 303.1–598.5 |
| isobaric heat capacity | 35 | 3 | 273.15–333.15 |
| thermal conductivity | 272 | 1 | 301.73–497.8 |

The combined interim dataset contains 540 measurements. All accepted records
have a liquid phase and source DOI.

## Rejections

- 305 gas-phase thermal-conductivity measurements are excluded from the
  pure-liquid interim dataset.
- 20 multicomponent ThermoML sections are excluded. Their `record_count` values
  preserve how many property values each rejected section contains.
- Rejections retain their source file, DOI, ThermoML record reference, reason,
  property label where available, and phase where available.

## Overlap result

- Density and dynamic viscosity overlap for one molecule.
- Density and isobaric heat capacity overlap for three molecules.
- Dynamic viscosity and isobaric heat capacity overlap for one molecule.
- No molecule currently has all four core properties.

This sample set is sufficient to validate multi-property ingestion behavior but
is not a final coverage audit and is not large enough for model training.

## Parser correction

Property alias matching now checks exact and longer aliases before broad
substrings. This prevents `kinematic viscosity` from being incorrectly labeled
as `dynamic_viscosity` through the shorter `viscosity` alias.
