# IFD-002 Parser Notes

## Sample Source

- File: `data/raw/thermoml/10.1021_acs.jced.5b00270.xml`
- DOI: `10.1021/acs.jced.5b00270`
- Title: `Viscosities of liquid cyclohexane and decane at temperatures between (303 and 598) K and pressures up to 4 MPa measured in a dual-capillary viscometer`
- Source type: ThermoML XML from the NIST ThermoML archive

## Build Command

```bash
PYTHONPATH=src python3 -m immersion_ml.data.build_dataset
```

## Parsed Result

- Parsed measurement rows: 94
- Property: `dynamic_viscosity`
- Molecules: `cyclohexane`, `decane`
- Temperature range: 303.1 K to 598.5 K
- Pressure range: 130000 Pa to 4030000 Pa
- Phase quality flags: all rows `ok`
- Source DOI retained for all rows
- Measurement method retained for all rows
- Expanded uncertainty retained for all rows

## Generated Outputs

The build command generated:

```text
data/interim/thermoml_raw_measurements.csv
reports/data_audit/coverage_report.csv
reports/data_audit/overlap_report.csv
```

These CSV files are intentionally ignored by Git because they are reproducible
from the raw ThermoML file and code.

## Parser Changes

The original tolerant XML parser could detect the real file but did not correctly
follow ThermoML's `Property`, `Variable`, and `NumValues` number references.

This ticket adds a structured ThermoML parsing path that:

- maps compounds by `nOrgNum`
- extracts pure-compound `PureOrMixtureData` sections only
- maps `nPropNumber` to property name, unit, method, and phase
- maps `nVarNumber` to temperature, pressure, and frequency variables
- emits one row per `PropertyValue`
- preserves DOI, publication year, source title, phase, method, and uncertainty

## Known Limitations

- This sample covers only dynamic viscosity.
- CAS numbers and SMILES are not present in this source file, so those fields are
  empty.
- Broader ThermoML property coverage still needs additional sample files in later
  tickets.

