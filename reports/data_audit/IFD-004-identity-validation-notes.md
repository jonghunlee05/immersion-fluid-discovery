# IFD-004 Identity Validation Notes

## Input preservation

The identity pipeline consumes the 4,637 accepted IFD-003 measurement rows and
writes 4,637 identity-enriched rows. It does not average, delete, or fabricate
experimental measurements. The original source-local `molecule_id` is retained
as `source_molecule_id`; the resolved `molecule_id` is the verified InChIKey.

## Resolution result

- 4,637 of 4,637 measurement rows resolve successfully.
- The rows form 135 unique RDKit-validated molecule identities.
- Every source-provided InChIKey matches the key regenerated from its InChI.
- No current measurement is unresolved or quarantined for an identity conflict.
- All 135 catalog entries are single-fragment, formally neutral structures.

The clean result reflects the strong identity metadata in the selected ThermoML
sources. It does not justify assuming future sources will resolve equally well;
the failure and conflict paths remain implemented and tested.

## Stereochemistry and environmental fields

Eight catalog identities contain one or more stereocenters whose configuration
is not specified by the source identity. They remain resolved but are marked
with `stereochemistry_status=unspecified` and an explicit unassigned-center
count. No stereochemistry is invented.

One current catalog molecule contains fluorine. It is retained and receives a
nonzero `fluorine_count`, because the project's PFAS versus fluorine-free rule
remains intentionally unresolved.

## Reproducibility

RDKit 2026.03.5 is pinned in both `pyproject.toml` and `requirements.txt`.
Generated identity CSVs remain ignored by Git and can be rebuilt from the
committed raw ThermoML files and version-controlled pipeline.
