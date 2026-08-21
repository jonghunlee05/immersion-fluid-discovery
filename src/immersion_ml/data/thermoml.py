"""Conservative ThermoML-style XML ingestion.

The parser is intentionally schema-tolerant: ThermoML files vary across versions
and exports, so this module extracts recognized text/value/unit patterns while
preserving missingness and provenance instead of fabricating values.
"""

from __future__ import annotations

import csv
import hashlib
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from immersion_ml.data.normalize import UnitConversionError, normalize_pressure
from immersion_ml.data.schema import RAW_MEASUREMENT_COLUMNS, RawMeasurement


TARGET_PROPERTY_ALIASES: dict[str, tuple[str, ...]] = {
    "thermal_conductivity": (
        "thermal conductivity",
        "coefficient of thermal conductivity",
    ),
    "dynamic_viscosity": ("viscosity", "dynamic viscosity"),
    "kinematic_viscosity": ("kinematic viscosity",),
    "density": ("density", "mass density"),
    "isobaric_heat_capacity": (
        "isobaric heat capacity",
        "heat capacity at constant pressure",
        "specific heat capacity",
    ),
    "vapor_pressure": ("vapor pressure", "vapour pressure"),
    "boiling_temperature": (
        "boiling temperature",
        "normal boiling temperature",
        "boiling point",
    ),
    "relative_permittivity": ("relative permittivity", "dielectric constant"),
}


LIQUID_TOKENS = ("liquid", "liq")


def parse_thermoml_file(path: str | Path) -> list[dict[str, Any]]:
    """Parse one ThermoML-style XML file into project raw-measurement rows."""

    xml_path = Path(path)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    structured_rows = _parse_structured_thermoml(root, xml_path)
    if structured_rows:
        return structured_rows

    source = _source_metadata(root, xml_path)
    compounds = _compound_metadata(root)
    rows: list[dict[str, Any]] = []

    for idx, node in enumerate(_candidate_measurement_nodes(root), start=1):
        measurement = _extract_measurement(node)
        property_name = canonical_property_name(measurement.get("property_label"))
        if property_name is None:
            continue

        phase = measurement.get("phase")
        quality_flag = _quality_flag_for_phase(phase)
        compound = _select_compound(measurement, compounds)
        record_id = _record_id(xml_path, idx, measurement)

        row = RawMeasurement(
            record_id=record_id,
            molecule_id=compound.get("molecule_id"),
            molecule_name=compound.get("molecule_name"),
            CAS=compound.get("CAS"),
            InChI=compound.get("InChI"),
            InChIKey=compound.get("InChIKey"),
            SMILES=compound.get("SMILES"),
            property_name=property_name,
            property_value=measurement.get("value"),
            property_unit=measurement.get("unit"),
            temperature_K=measurement.get("temperature_K"),
            pressure_Pa=measurement.get("pressure_Pa"),
            phase=phase,
            frequency_Hz=measurement.get("frequency_Hz"),
            measurement_method=measurement.get("method"),
            uncertainty=measurement.get("uncertainty"),
            uncertainty_type=measurement.get("uncertainty_type"),
            source_type="ThermoML",
            source_title=source.get("source_title"),
            source_DOI=source.get("source_DOI"),
            source_url=source.get("source_url"),
            publication_year=source.get("publication_year"),
            source_record_id=measurement.get("source_record_id"),
            notes=measurement.get("notes"),
            quality_flag=quality_flag,
        )
        rows.append(row.to_row())

    return rows


def _parse_structured_thermoml(root: ET.Element, xml_path: Path) -> list[dict[str, Any]]:
    """Parse ThermoML DataReport records using property/variable number links."""

    source = _source_metadata(root, xml_path)
    compounds = _structured_compounds(root)
    rows: list[dict[str, Any]] = []

    for data_node in _children_by_name(root, "PureOrMixtureData"):
        components = _children_by_name(data_node, "Component")
        if len(components) != 1:
            continue

        org_num = _descendant_text(components[0], "nOrgNum")
        compound = compounds.get(org_num or "", {})
        properties = _structured_properties(data_node)
        variables = _structured_variables(data_node)
        phase = _descendant_text(data_node, "ePhase")
        data_number = _child_text(data_node, "nPureOrMixtureDataNumber")

        for value_idx, values_node in enumerate(_children_by_name(data_node, "NumValues"), start=1):
            variable_values = _structured_variable_values(values_node, variables)
            for property_value_node in _children_by_name(values_node, "PropertyValue"):
                property_number = _child_text(property_value_node, "nPropNumber")
                property_definition = properties.get(property_number or "")
                if not property_definition:
                    continue

                property_name = canonical_property_name(property_definition.get("label"))
                if property_name is None:
                    continue

                measurement_value = _parse_float(_child_text(property_value_node, "nPropValue"))
                uncertainty = _parse_float(
                    _descendant_text(property_value_node, "nCombExpandUncertValue")
                )
                record_id = _record_id(
                    xml_path,
                    len(rows) + 1,
                    {
                        "property_label": property_definition.get("label"),
                        "value": measurement_value,
                        "temperature_K": variable_values.get("temperature_K"),
                    },
                )

                row = RawMeasurement(
                    record_id=record_id,
                    molecule_id=compound.get("molecule_id"),
                    molecule_name=compound.get("molecule_name"),
                    CAS=compound.get("CAS"),
                    InChI=compound.get("InChI"),
                    InChIKey=compound.get("InChIKey"),
                    SMILES=compound.get("SMILES"),
                    property_name=property_name,
                    property_value=measurement_value,
                    property_unit=property_definition.get("unit"),
                    temperature_K=variable_values.get("temperature_K"),
                    pressure_Pa=variable_values.get("pressure_Pa"),
                    phase=property_definition.get("phase") or phase,
                    frequency_Hz=variable_values.get("frequency_Hz"),
                    measurement_method=property_definition.get("method"),
                    uncertainty=uncertainty,
                    uncertainty_type="expanded" if uncertainty is not None else None,
                    source_type="ThermoML",
                    source_title=source.get("source_title"),
                    source_DOI=source.get("source_DOI"),
                    source_url=source.get("source_url"),
                    publication_year=source.get("publication_year"),
                    source_record_id=_join_nonempty(
                        [
                            f"PureOrMixtureData={data_number}" if data_number else None,
                            f"NumValues={value_idx}",
                            f"Property={property_number}" if property_number else None,
                        ]
                    ),
                    quality_flag=_quality_flag_for_phase(property_definition.get("phase") or phase),
                )
                rows.append(row.to_row())

    return rows


def _structured_compounds(root: ET.Element) -> dict[str, dict[str, Any]]:
    compounds: dict[str, dict[str, Any]] = {}
    for node in _children_by_name(root, "Compound"):
        org_num = _descendant_text(node, "nOrgNum")
        if not org_num:
            continue
        common_names = _child_texts(node, "sCommonName")
        compounds[org_num] = {
            "molecule_id": org_num,
            "molecule_name": common_names[0] if common_names else None,
            "CAS": _structured_cas(node),
            "InChI": _child_text(node, "sStandardInChI"),
            "InChIKey": _child_text(node, "sStandardInChIKey"),
            "SMILES": None,
        }
    return compounds


def _structured_properties(data_node: ET.Element) -> dict[str, dict[str, str | None]]:
    properties: dict[str, dict[str, str | None]] = {}
    for node in _children_by_name(data_node, "Property"):
        property_number = _child_text(node, "nPropNumber")
        label = _descendant_text(node, "ePropName")
        method = _descendant_text(node, "eMethodName")
        phase = _descendant_text(node, "ePropPhase")
        if property_number and label:
            properties[property_number] = {
                "label": label,
                "unit": _unit_from_label(label),
                "method": method,
                "phase": phase,
            }
    return properties


def _structured_variables(data_node: ET.Element) -> dict[str, dict[str, str | None]]:
    variables: dict[str, dict[str, str | None]] = {}
    for node in _children_by_name(data_node, "Variable"):
        variable_number = _child_text(node, "nVarNumber")
        label = (
            _descendant_text(node, "eTemperature")
            or _descendant_text(node, "ePressure")
            or _descendant_text(node, "eFrequency")
        )
        if variable_number and label:
            variables[variable_number] = {
                "label": label,
                "unit": _unit_from_label(label),
            }
    return variables


def _structured_variable_values(
    values_node: ET.Element, variables: dict[str, dict[str, str | None]]
) -> dict[str, float | None]:
    values: dict[str, float | None] = {
        "temperature_K": None,
        "pressure_Pa": None,
        "frequency_Hz": None,
    }
    for node in _children_by_name(values_node, "VariableValue"):
        variable_number = _child_text(node, "nVarNumber")
        variable_definition = variables.get(variable_number or "")
        raw_value = _parse_float(_child_text(node, "nVarValue"))
        if not variable_definition or raw_value is None:
            continue

        label = (variable_definition.get("label") or "").lower()
        unit = variable_definition.get("unit")
        if "temperature" in label:
            values["temperature_K"] = _temperature_to_kelvin(raw_value, unit)
        elif "pressure" in label:
            try:
                values["pressure_Pa"] = normalize_pressure(raw_value, unit or "Pa")
            except UnitConversionError:
                values["pressure_Pa"] = None
        elif "frequency" in label:
            values["frequency_Hz"] = _frequency_to_hz(raw_value, unit)
    return values


def parse_thermoml_directory(path: str | Path) -> list[dict[str, Any]]:
    """Parse all XML files under a directory into raw-measurement rows."""

    root = Path(path)
    rows: list[dict[str, Any]] = []
    for xml_path in sorted(root.rglob("*.xml")):
        rows.extend(parse_thermoml_file(xml_path))
    return rows


def write_raw_measurements_csv(rows: Sequence[dict[str, Any]], path: str | Path) -> None:
    """Write raw measurement rows using the canonical column order."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_MEASUREMENT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in RAW_MEASUREMENT_COLUMNS})


def canonical_property_name(label: str | None) -> str | None:
    if not label:
        return None
    normalized_label = _clean_text(label).lower()
    for canonical, aliases in TARGET_PROPERTY_ALIASES.items():
        if any(alias in normalized_label for alias in aliases):
            return canonical
    return None


def _candidate_measurement_nodes(root: ET.Element) -> Iterable[ET.Element]:
    candidates = [
        node
        for node in root.iter()
        if canonical_property_name(_element_text_blob(node)) is not None
        and _extract_value_and_unit(node)[0] is not None
    ]
    for node in root.iter():
        if node not in candidates:
            continue
        if any(descendant in candidates for descendant in node.iter() if descendant is not node):
            continue
        yield node


def _extract_measurement(node: ET.Element) -> dict[str, Any]:
    text = _element_text_blob(node)
    value, unit = _extract_value_and_unit(node)
    temp_value, temp_unit = _find_value_near_labels(node, ("temperature", "temp"))
    pressure_value, pressure_unit = _find_value_near_labels(node, ("pressure",))
    frequency_value, frequency_unit = _find_value_near_labels(node, ("frequency",))

    pressure_pa = None
    if pressure_value is not None and pressure_unit:
        try:
            pressure_pa = normalize_pressure(pressure_value, pressure_unit)
        except UnitConversionError:
            pressure_pa = None

    return {
        "property_label": text,
        "value": value,
        "unit": unit,
        "temperature_K": _temperature_to_kelvin(temp_value, temp_unit),
        "pressure_Pa": pressure_pa,
        "frequency_Hz": _frequency_to_hz(frequency_value, frequency_unit),
        "phase": _find_text_near_labels(node, ("phase", "state")),
        "method": _find_text_near_labels(node, ("method", "technique")),
        "uncertainty": _find_float_near_labels(node, ("uncertainty", "error")),
        "uncertainty_type": _find_text_near_labels(node, ("uncertainty type", "error type")),
        "source_record_id": _first_attr_or_text(node, ("id", "recordid", "record_id")),
        "notes": None,
    }


def _compound_metadata(root: ET.Element) -> list[dict[str, Any]]:
    compounds: list[dict[str, Any]] = []
    for node in root.iter():
        tag = _local_name(node.tag).lower()
        if "compound" not in tag and "component" not in tag and "substance" not in tag:
            continue
        blob = _element_text_blob(node)
        if not blob:
            continue
        metadata = {
            "molecule_id": _first_attr_or_text(node, ("id", "compoundid", "componentid")),
            "molecule_name": _find_text_near_labels(node, ("name", "compound name", "iupac")),
            "CAS": _extract_cas(blob),
            "InChI": _extract_prefixed_value(blob, "InChI"),
            "InChIKey": _extract_prefixed_value(blob, "InChIKey"),
            "SMILES": _extract_prefixed_value(blob, "SMILES"),
        }
        if any(metadata.values()):
            compounds.append(metadata)
    return compounds


def _select_compound(
    measurement: dict[str, Any], compounds: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    if len(compounds) == 1:
        return dict(compounds[0])
    source_id = measurement.get("source_record_id")
    if source_id:
        for compound in compounds:
            if compound.get("molecule_id") == source_id:
                return dict(compound)
    return {}


def _source_metadata(root: ET.Element, path: Path) -> dict[str, Any]:
    blob = _element_text_blob(root)
    return {
        "source_title": _find_text_near_labels(root, ("title", "article title")) or path.name,
        "source_DOI": _extract_doi(blob),
        "source_url": None,
        "publication_year": _extract_year(blob),
    }


def _quality_flag_for_phase(phase: str | None) -> str | None:
    if phase is None:
        return "phase_missing"
    normalized = phase.lower()
    if any(token in normalized for token in LIQUID_TOKENS):
        return None
    return "non_liquid_or_ambiguous_phase"


def _record_id(path: Path, idx: int, measurement: dict[str, Any]) -> str:
    seed = "|".join(
        [
            str(path),
            str(idx),
            str(measurement.get("property_label")),
            str(measurement.get("value")),
            str(measurement.get("temperature_K")),
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"thermoml:{path.stem}:{idx}:{digest}"


def _element_text_blob(node: ET.Element) -> str:
    parts = []
    for item in node.iter():
        if item.text and item.text.strip():
            parts.append(item.text.strip())
        if item.tail and item.tail.strip():
            parts.append(item.tail.strip())
    return _clean_text(" ".join(parts))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children_by_name(node: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in node if _local_name(child.tag) == name]


def _child_text(node: ET.Element, name: str) -> str | None:
    for child in node:
        if _local_name(child.tag) == name and child.text and child.text.strip():
            return _clean_text(child.text)
    return None


def _child_texts(node: ET.Element, name: str) -> list[str]:
    return [
        _clean_text(child.text)
        for child in node
        if _local_name(child.tag) == name and child.text and child.text.strip()
    ]


def _descendant_text(node: ET.Element, name: str) -> str | None:
    for child in node.iter():
        if _local_name(child.tag) == name and child.text and child.text.strip():
            return _clean_text(child.text)
    return None


def _unit_from_label(label: str | None) -> str | None:
    if not label or "," not in label:
        return None
    return _clean_text(label.rsplit(",", 1)[-1])


def _structured_cas(node: ET.Element) -> str | None:
    for reg_num in node.iter():
        if _local_name(reg_num.tag) != "RegNum":
            continue
        cas_blob = "-".join(
            value
            for key in ("nCASNumBeg", "nCASNumMid", "nCASNumEnd")
            if (value := _child_text(reg_num, key))
        )
        if cas_blob.count("-") == 2:
            return cas_blob
    return None


def _join_nonempty(values: Sequence[str | None], separator: str = ";") -> str | None:
    present = [value for value in values if value]
    return separator.join(present) if present else None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_float_from_node(node: ET.Element) -> float | None:
    for item in node.iter():
        candidates = []
        if item.text:
            candidates.append(item.text)
        candidates.extend(item.attrib.values())
        for candidate in candidates:
            parsed = _parse_float(candidate)
            if parsed is not None:
                return parsed
    return None


def _extract_value_and_unit(node: ET.Element) -> tuple[float | None, str | None]:
    excluded_tags = ("temperature", "pressure", "frequency", "uncertainty", "error")
    for item in node.iter():
        tag = _local_name(item.tag).lower()
        if any(excluded in tag for excluded in excluded_tags):
            continue
        if "value" not in tag and "num" not in tag:
            continue
        value = _extract_float_from_node(item)
        if value is not None:
            return value, _unit_from_node(item)
    return None, None


def _find_value_near_labels(
    node: ET.Element, labels: tuple[str, ...]
) -> tuple[float | None, str | None]:
    for item in node.iter():
        item_blob = _clean_text(" ".join([_local_name(item.tag), *(item.attrib.values())]))
        if any(label in item_blob.lower() for label in labels):
            value = _extract_float_from_node(item)
            unit = _unit_from_node(item)
            return value, unit
    return None, None


def _find_float_near_labels(node: ET.Element, labels: tuple[str, ...]) -> float | None:
    value, _unit = _find_value_near_labels(node, labels)
    return value


def _find_text_near_labels(node: ET.Element, labels: tuple[str, ...]) -> str | None:
    for item in node.iter():
        tag = _local_name(item.tag).lower()
        attr_blob = " ".join(f"{key} {value}" for key, value in item.attrib.items()).lower()
        if any(label in tag or label in attr_blob for label in labels):
            if item.text and item.text.strip():
                return _clean_text(item.text)
            for attr_value in item.attrib.values():
                if attr_value.strip():
                    return _clean_text(attr_value)
    return None


def _unit_from_node(node: ET.Element) -> str | None:
    for key, value in node.attrib.items():
        if "unit" in key.lower() and value.strip():
            return _clean_text(value)
    for item in node.iter():
        tag = _local_name(item.tag).lower()
        if "unit" in tag:
            if item.text and item.text.strip():
                return _clean_text(item.text)
            for attr_value in item.attrib.values():
                if attr_value.strip():
                    return _clean_text(attr_value)
    return None


def _first_attr_or_text(node: ET.Element, names: tuple[str, ...]) -> str | None:
    lowered = {key.lower(): value for key, value in node.attrib.items()}
    for name in names:
        if name.lower() in lowered:
            return lowered[name.lower()]
    return None


def _parse_float(value: object) -> float | None:
    if value is None:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _temperature_to_kelvin(value: float | None, unit: str | None) -> float | None:
    if value is None:
        return None
    if unit is None:
        return value
    normalized = unit.strip().lower()
    if normalized in {"k", "kelvin"}:
        return value
    if normalized in {"c", "degc", "°c"}:
        return value + 273.15
    if normalized in {"f", "degf", "°f"}:
        return (value - 32.0) * 5.0 / 9.0 + 273.15
    return None


def _frequency_to_hz(value: float | None, unit: str | None) -> float | None:
    if value is None:
        return None
    if unit is None:
        return value
    normalized = unit.strip().lower()
    factors = {"hz": 1.0, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
    return value * factors[normalized] if normalized in factors else None


def _extract_cas(blob: str) -> str | None:
    match = re.search(r"\b\d{2,7}-\d{2}-\d\b", blob)
    return match.group(0) if match else None


def _extract_doi(blob: str) -> str | None:
    match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", blob)
    return match.group(0) if match else None


def _extract_year(blob: str) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", blob)
    return int(match.group(0)) if match else None


def _extract_prefixed_value(blob: str, prefix: str) -> str | None:
    pattern = rf"{re.escape(prefix)}\s*[:=]\s*([^\s,;]+)"
    match = re.search(pattern, blob, flags=re.IGNORECASE)
    return match.group(1) if match else None
