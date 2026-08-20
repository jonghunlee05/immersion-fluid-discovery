"""Unit normalization utilities for processed/interim experimental data."""

from __future__ import annotations

from typing import Callable


class UnitConversionError(ValueError):
    """Raised when a unit conversion is unsupported or invalid."""


def _normalize_unit(unit: str | None) -> str:
    if unit is None:
        raise UnitConversionError("Missing unit cannot be normalized.")
    return (
        unit.strip()
        .replace(" ", "")
        .replace("·", "*")
        .replace("−", "-")
        .replace("⁻¹", "^-1")
        .replace("⁻³", "^-3")
    )


def celsius_to_kelvin(value: float) -> float:
    return value + 273.15


def fahrenheit_to_kelvin(value: float) -> float:
    return (value - 32.0) * 5.0 / 9.0 + 273.15


def normalize_temperature(value: float, unit: str) -> float:
    normalized = _normalize_unit(unit).lower()
    converters: dict[str, Callable[[float], float]] = {
        "k": lambda x: x,
        "kelvin": lambda x: x,
        "c": celsius_to_kelvin,
        "degc": celsius_to_kelvin,
        "°c": celsius_to_kelvin,
        "f": fahrenheit_to_kelvin,
        "degf": fahrenheit_to_kelvin,
        "°f": fahrenheit_to_kelvin,
    }
    try:
        return converters[normalized](value)
    except KeyError as exc:
        raise UnitConversionError(f"Unsupported temperature unit: {unit}") from exc


def normalize_pressure(value: float, unit: str) -> float:
    normalized = _normalize_unit(unit).lower()
    factors = {
        "pa": 1.0,
        "kpa": 1_000.0,
        "mpa": 1_000_000.0,
        "bar": 100_000.0,
        "mbar": 100.0,
        "atm": 101_325.0,
        "mmhg": 133.322368,
        "torr": 133.322368,
    }
    try:
        return value * factors[normalized]
    except KeyError as exc:
        raise UnitConversionError(f"Unsupported pressure unit: {unit}") from exc


def normalize_property_value(property_name: str, value: float, unit: str) -> float:
    """Normalize supported property values to project canonical units."""

    property_key = property_name.strip().lower()
    normalized_unit = _normalize_unit(unit).lower()

    if property_key in {"thermal_conductivity", "thermal conductivity"}:
        if normalized_unit in {"w/(m*k)", "w*m^-1*k^-1", "w/m/k"}:
            return value
    elif property_key in {"dynamic_viscosity", "dynamic viscosity", "viscosity"}:
        if normalized_unit in {"pa*s", "pas"}:
            return value
        if normalized_unit in {"mpa*s", "mpas", "cp"}:
            return value * 0.001
    elif property_key in {"kinematic_viscosity", "kinematic viscosity"}:
        if normalized_unit in {"m^2/s", "m2/s"}:
            return value
        if normalized_unit in {"mm^2/s", "mm2/s", "cst"}:
            return value * 1e-6
    elif property_key == "density":
        if normalized_unit in {"kg/m^3", "kg*m^-3"}:
            return value
        if normalized_unit in {"g/cm^3", "g*cm^-3"}:
            return value * 1_000.0
    elif property_key in {"isobaric_heat_capacity", "heat capacity", "specific heat capacity"}:
        if normalized_unit in {"j/(kg*k)", "j*kg^-1*k^-1"}:
            return value
        if normalized_unit in {"kj/(kg*k)", "kj*kg^-1*k^-1"}:
            return value * 1_000.0
    elif property_key in {"vapor_pressure", "vapor pressure", "vapour pressure"}:
        return normalize_pressure(value, unit)
    elif property_key in {"boiling_temperature", "boiling temperature", "boiling point"}:
        return normalize_temperature(value, unit)
    elif property_key in {"relative_permittivity", "relative permittivity", "dielectric constant"}:
        if normalized_unit in {"dimensionless", "1", ""}:
            return value

    raise UnitConversionError(
        f"Unsupported conversion for property '{property_name}' with unit '{unit}'."
    )


def dynamic_viscosity_from_kinematic(
    kinematic_viscosity_m2_s: float, density_kg_m3: float
) -> float:
    """Convert kinematic viscosity to dynamic viscosity using mu = rho * nu."""

    return density_kg_m3 * kinematic_viscosity_m2_s

