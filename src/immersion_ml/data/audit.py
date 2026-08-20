"""Coverage and overlap reports for experimental measurement rows."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path
from statistics import median
from typing import Any


COVERAGE_COLUMNS = [
    "property_name",
    "measurement_count",
    "unique_molecule_count",
    "temperature_min_K",
    "temperature_max_K",
    "pressure_min_Pa",
    "pressure_max_Pa",
    "median_measurements_per_molecule",
    "missing_temperature_count",
    "missing_pressure_count",
    "missing_phase_count",
    "missing_source_doi_count",
    "source_distribution",
    "quality_flag_distribution",
]

OVERLAP_COLUMNS = ["property_set", "property_count", "unique_molecule_count"]


def load_measurements_csv(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def coverage_report(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize coverage by property without averaging measurements."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        property_name = row.get("property_name")
        if property_name:
            grouped[str(property_name)].append(row)

    report: list[dict[str, Any]] = []
    for property_name, property_rows in sorted(grouped.items()):
        molecule_ids = [_molecule_key(row) for row in property_rows if _molecule_key(row)]
        temperatures = [_to_float(row.get("temperature_K")) for row in property_rows]
        temperatures = [value for value in temperatures if value is not None]
        pressures = [_to_float(row.get("pressure_Pa")) for row in property_rows]
        pressures = [value for value in pressures if value is not None]
        counts_by_molecule = Counter(molecule_ids)
        source_types = Counter(row.get("source_type") or "missing" for row in property_rows)

        report.append(
            {
                "property_name": property_name,
                "measurement_count": len(property_rows),
                "unique_molecule_count": len(set(molecule_ids)),
                "temperature_min_K": min(temperatures) if temperatures else None,
                "temperature_max_K": max(temperatures) if temperatures else None,
                "pressure_min_Pa": min(pressures) if pressures else None,
                "pressure_max_Pa": max(pressures) if pressures else None,
                "median_measurements_per_molecule": (
                    median(counts_by_molecule.values()) if counts_by_molecule else None
                ),
                "missing_temperature_count": _missing_count(property_rows, "temperature_K"),
                "missing_pressure_count": _missing_count(property_rows, "pressure_Pa"),
                "missing_phase_count": _missing_count(property_rows, "phase"),
                "missing_source_doi_count": _missing_count(property_rows, "source_DOI"),
                "source_distribution": dict(sorted(source_types.items())),
                "quality_flag_distribution": dict(
                    sorted(
                        Counter(row.get("quality_flag") or "ok" for row in property_rows).items()
                    )
                ),
            }
        )
    return report


def overlap_report(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Measure cross-property molecule overlap for all observed properties."""

    property_to_molecules: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        property_name = row.get("property_name")
        molecule_key = _molecule_key(row)
        if property_name and molecule_key:
            property_to_molecules[str(property_name)].add(molecule_key)

    properties = sorted(property_to_molecules)
    report: list[dict[str, Any]] = []
    for idx, left in enumerate(properties):
        for right in properties[idx:]:
            left_set = property_to_molecules[left]
            right_set = property_to_molecules[right]
            intersection = left_set & right_set
            report.append(
                {
                    "property_set": "|".join([left, right]) if left != right else left,
                    "property_count": 1 if left == right else 2,
                    "unique_molecule_count": len(intersection),
                }
            )

    core = ["thermal_conductivity", "dynamic_viscosity", "density", "isobaric_heat_capacity"]
    present_core = [name for name in core if name in property_to_molecules]
    if len(present_core) >= 3:
        shared = set.intersection(*(property_to_molecules[name] for name in present_core))
        report.append(
            {
                "property_set": "|".join(present_core),
                "property_count": len(present_core),
                "unique_molecule_count": len(shared),
            }
        )

    return report


def write_report_csv(rows: Sequence[dict[str, Any]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if "coverage" in output_path.name:
        fieldnames = COVERAGE_COLUMNS
    elif "overlap" in output_path.name:
        fieldnames = OVERLAP_COLUMNS
    else:
        fieldnames = _fieldnames(rows)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: Sequence[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _molecule_key(row: dict[str, Any]) -> str | None:
    for key in ("InChIKey", "canonical_SMILES", "SMILES", "CAS", "molecule_id", "molecule_name"):
        value = row.get(key)
        if value:
            return str(value)
    return None


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _missing_count(rows: Sequence[dict[str, Any]], key: str) -> int:
    return sum(1 for row in rows if row.get(key) in (None, ""))
