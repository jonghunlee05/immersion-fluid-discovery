"""Canonical raw-measurement schema for experimental property records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


RAW_MEASUREMENT_COLUMNS: tuple[str, ...] = (
    "record_id",
    "molecule_id",
    "molecule_name",
    "CAS",
    "InChI",
    "InChIKey",
    "SMILES",
    "canonical_SMILES",
    "property_name",
    "property_value",
    "property_unit",
    "temperature_K",
    "pressure_Pa",
    "phase",
    "frequency_Hz",
    "measurement_method",
    "uncertainty",
    "uncertainty_type",
    "source_type",
    "source_title",
    "source_DOI",
    "source_url",
    "publication_year",
    "source_record_id",
    "notes",
    "quality_flag",
)


@dataclass(frozen=True)
class RawMeasurement:
    """One experimental measurement row with explicit provenance."""

    record_id: str
    molecule_id: str | None = None
    molecule_name: str | None = None
    CAS: str | None = None
    InChI: str | None = None
    InChIKey: str | None = None
    SMILES: str | None = None
    canonical_SMILES: str | None = None
    property_name: str | None = None
    property_value: float | None = None
    property_unit: str | None = None
    temperature_K: float | None = None
    pressure_Pa: float | None = None
    phase: str | None = None
    frequency_Hz: float | None = None
    measurement_method: str | None = None
    uncertainty: float | None = None
    uncertainty_type: str | None = None
    source_type: str | None = None
    source_title: str | None = None
    source_DOI: str | None = None
    source_url: str | None = None
    publication_year: int | None = None
    source_record_id: str | None = None
    notes: str | None = None
    quality_flag: str | None = None

    def to_row(self) -> dict[str, Any]:
        """Return a dict with columns in the project-specified order."""

        row = asdict(self)
        return {column: row.get(column) for column in RAW_MEASUREMENT_COLUMNS}


def empty_raw_row(record_id: str) -> dict[str, Any]:
    """Create an empty raw-measurement row with the required record id."""

    return RawMeasurement(record_id=record_id).to_row()

