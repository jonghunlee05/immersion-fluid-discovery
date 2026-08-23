"""Resolve measurement identities into a validated molecule catalog."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from immersion_ml.chemistry.rdkit_validation import (
    StructureValidationError,
    ValidatedStructure,
    validate_structure,
)
from immersion_ml.data.schema import RAW_MEASUREMENT_COLUMNS


IDENTITY_MEASUREMENT_COLUMNS = (
    *RAW_MEASUREMENT_COLUMNS,
    "source_molecule_id",
    "identity_status",
    "identity_method",
    "identity_notes",
)

MOLECULE_CATALOG_COLUMNS = (
    "molecule_id",
    "preferred_name",
    "source_names",
    "source_CAS",
    "source_InChI",
    "source_InChIKey",
    "canonical_SMILES",
    "isomeric_SMILES",
    "RDKit_InChI",
    "RDKit_InChIKey",
    "molecular_formula",
    "molecular_weight",
    "logP",
    "TPSA",
    "atom_count",
    "heavy_atom_count",
    "ring_count",
    "heteroatom_count",
    "fluorine_count",
    "formal_charge",
    "rotatable_bond_count",
    "fragment_count",
    "stereocenter_count",
    "unassigned_stereocenter_count",
    "stereochemistry_status",
    "identity_status",
    "identity_method",
    "measurement_count",
    "source_DOIs",
)

IDENTITY_REPORT_COLUMNS = (
    "identity_status",
    "measurement_count",
    "unique_molecule_count",
    "notes",
)

IDENTITY_ISSUE_COLUMNS = (
    "record_id",
    "molecule_name",
    "source_DOI",
    "source_record_id",
    "issue",
    "provided_InChIKey",
    "derived_InChIKey",
    "notes",
)


def resolve_measurement_identities(
    rows: Iterable[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Enrich all rows and return resolved rows, catalog, report, and issues."""

    input_rows = list(rows)
    cache: dict[tuple[str, str], ValidatedStructure | StructureValidationError] = {}
    resolved_rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    for source_row in input_rows:
        row = {column: source_row.get(column) for column in RAW_MEASUREMENT_COLUMNS}
        row["source_molecule_id"] = row.get("molecule_id")
        row["molecule_id"] = ""
        inchi = _text(row.get("InChI"))
        smiles = _text(row.get("SMILES"))
        method = "source_InChI" if inchi else "source_SMILES" if smiles else "unresolved"
        cache_key = (inchi or "", smiles or "")
        result = cache.get(cache_key)
        if result is None:
            try:
                result = validate_structure(inchi=inchi, smiles=smiles)
            except StructureValidationError as exc:
                result = exc
            cache[cache_key] = result

        if isinstance(result, StructureValidationError):
            status = "unresolved"
            note = str(result)
            issues.append(_issue_row(row, note, derived_inchikey=None))
        else:
            supplied_key = _text(row.get("InChIKey"))
            if supplied_key and supplied_key != result.inchikey:
                status = "conflict"
                note = "source_InChIKey_does_not_match_RDKit"
                issues.append(_issue_row(row, note, derived_inchikey=result.inchikey))
            else:
                status = "resolved"
                note = ""
                row["molecule_id"] = result.inchikey
                row["canonical_SMILES"] = result.canonical_smiles

        row["identity_status"] = status
        row["identity_method"] = method
        row["identity_notes"] = note
        resolved_rows.append(row)

    catalog = _molecule_catalog(resolved_rows, cache)
    report = _identity_report(resolved_rows, catalog)
    return resolved_rows, catalog, report, issues


def write_csv(
    rows: Sequence[dict[str, Any]], path: str | Path, fieldnames: Sequence[str]
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _molecule_catalog(
    rows: Sequence[dict[str, Any]],
    cache: dict[tuple[str, str], ValidatedStructure | StructureValidationError],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    structures: dict[str, ValidatedStructure] = {}
    for row in rows:
        if row.get("identity_status") != "resolved":
            continue
        molecule_id = str(row["molecule_id"])
        grouped[molecule_id].append(row)
        cache_key = (_text(row.get("InChI")) or "", _text(row.get("SMILES")) or "")
        structure = cache[cache_key]
        if isinstance(structure, ValidatedStructure):
            structures[molecule_id] = structure

    catalog: list[dict[str, Any]] = []
    for molecule_id, molecule_rows in sorted(grouped.items()):
        structure = structures[molecule_id]
        names = _unique_values(molecule_rows, "molecule_name")
        catalog.append(
            {
                "molecule_id": molecule_id,
                "preferred_name": names[0] if names else "",
                "source_names": "|".join(names),
                "source_CAS": "|".join(_unique_values(molecule_rows, "CAS")),
                "source_InChI": "|".join(_unique_values(molecule_rows, "InChI")),
                "source_InChIKey": "|".join(_unique_values(molecule_rows, "InChIKey")),
                "canonical_SMILES": structure.canonical_smiles,
                "isomeric_SMILES": structure.isomeric_smiles,
                "RDKit_InChI": structure.inchi,
                "RDKit_InChIKey": structure.inchikey,
                "molecular_formula": structure.molecular_formula,
                "molecular_weight": structure.molecular_weight,
                "logP": structure.logp,
                "TPSA": structure.tpsa,
                "atom_count": structure.atom_count,
                "heavy_atom_count": structure.heavy_atom_count,
                "ring_count": structure.ring_count,
                "heteroatom_count": structure.heteroatom_count,
                "fluorine_count": structure.fluorine_count,
                "formal_charge": structure.formal_charge,
                "rotatable_bond_count": structure.rotatable_bond_count,
                "fragment_count": structure.fragment_count,
                "stereocenter_count": structure.stereocenter_count,
                "unassigned_stereocenter_count": structure.unassigned_stereocenter_count,
                "stereochemistry_status": structure.stereochemistry_status,
                "identity_status": "resolved",
                "identity_method": "source_InChI_or_SMILES_plus_RDKit",
                "measurement_count": len(molecule_rows),
                "source_DOIs": "|".join(_unique_values(molecule_rows, "source_DOI")),
            }
        )
    return catalog


def _identity_report(
    rows: Sequence[dict[str, Any]], catalog: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    status_counts = Counter(str(row.get("identity_status") or "missing") for row in rows)
    notes = {
        "resolved": "Sanitized by RDKit and assigned a derived InChIKey molecule_id.",
        "conflict": "Source identifier conflicts with the RDKit-derived identity.",
        "unresolved": "No usable source structure or RDKit validation failed.",
    }
    report = []
    for status in ("resolved", "conflict", "unresolved"):
        status_rows = [row for row in rows if row.get("identity_status") == status]
        unique_ids = {row.get("molecule_id") for row in status_rows if row.get("molecule_id")}
        report.append(
            {
                "identity_status": status,
                "measurement_count": status_counts.get(status, 0),
                "unique_molecule_count": len(unique_ids) if status != "resolved" else len(catalog),
                "notes": notes[status],
            }
        )
    return report


def _issue_row(
    row: dict[str, Any], issue: str, derived_inchikey: str | None
) -> dict[str, Any]:
    return {
        "record_id": row.get("record_id"),
        "molecule_name": row.get("molecule_name"),
        "source_DOI": row.get("source_DOI"),
        "source_record_id": row.get("source_record_id"),
        "issue": issue,
        "provided_InChIKey": row.get("InChIKey"),
        "derived_InChIKey": derived_inchikey,
        "notes": "Measurement retained; no resolved molecule_id assigned.",
    }


def _unique_values(rows: Sequence[dict[str, Any]], key: str) -> list[str]:
    return sorted({_text(row.get(key)) for row in rows if _text(row.get(key))})


def _text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    cleaned = str(value).strip()
    return cleaned or None
