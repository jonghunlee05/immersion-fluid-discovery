"""Discover pure-property candidate sources through the NIST ThermoML API."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from immersion_ml.data.download import load_source_registry
from immersion_ml.data.thermoml import TARGET_PROPERTY_ALIASES, canonical_property_name


API_URL = "https://trc.nist.gov/ThermoML-API/objects"
CANDIDATE_COLUMNS = (
    "target_property",
    "DOI",
    "title",
    "publication_year",
    "source_url",
    "pure_target_data_points",
    "compound_count",
    "compound_names",
    "already_registered",
)


def query_archive(target_property: str, page_size: int = 100) -> list[dict[str, Any]]:
    if target_property not in TARGET_PROPERTY_ALIASES:
        raise ValueError(f"Unknown target property: {target_property}")
    search_label = TARGET_PROPERTY_ALIASES[target_property][0]
    parameters = urllib.parse.urlencode(
        {
            "query": f'type:TRCTml4 AND ("{search_label}")',
            "pageNum": 0,
            "pageSize": page_size,
            "sortFields": "",
            "requestContext": json.dumps(
                {"Citation": True, "data_summary": True, "Compound": True},
                separators=(",", ":"),
            ),
        }
    )
    request = urllib.request.Request(
        f"{API_URL}?{parameters}",
        headers={"User-Agent": "immersion-fluid-discovery/0.1 (ThermoML research audit)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    candidates = [
        candidate
        for result in payload.get("results", [])
        if (candidate := candidate_from_content(result.get("content", {}), target_property))
    ]
    return candidates


def candidate_from_content(
    content: dict[str, Any], target_property: str
) -> dict[str, Any] | None:
    citation = content.get("Citation") or {}
    doi = citation.get("sDOI")
    pure_summary = (content.get("data_summary") or {}).get("pure") or {}
    data_points = _target_data_points(pure_summary, target_property)
    if not doi or data_points < 1:
        return None

    names = []
    for compound in content.get("Compound") or []:
        common_names = compound.get("sCommonName") or []
        if common_names:
            names.append(str(common_names[0]))
    return {
        "target_property": target_property,
        "DOI": doi,
        "title": citation.get("sTitle"),
        "publication_year": citation.get("yrPubYr"),
        "source_url": f"https://trc.nist.gov/ThermoML/{doi}.xml",
        "pure_target_data_points": data_points,
        "compound_count": len(names),
        "compound_names": "|".join(names),
        "already_registered": False,
    }


def _target_data_points(summary: dict[str, Any], target_property: str) -> int:
    total = 0
    for label, value in summary.items():
        if canonical_property_name(label) == target_property and isinstance(value, dict):
            total += int(value.get("data_points") or 0)
        elif isinstance(value, dict):
            total += _target_data_points(value, target_property)
    return total


def write_candidates_csv(rows: list[dict[str, Any]], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find pure-property source candidates in the NIST ThermoML API."
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        choices=sorted(TARGET_PROPERTY_ALIASES),
        default=sorted(TARGET_PROPERTY_ALIASES),
    )
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("references/thermoml_source_registry.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/data_audit/thermoml_candidate_sources.csv"),
    )
    args = parser.parse_args()

    registered_dois = {
        source["DOI"] for source in load_source_registry(args.registry) if source.get("DOI")
    }
    candidates: list[dict[str, Any]] = []
    for target in args.targets:
        for candidate in query_archive(target, args.page_size):
            candidate["already_registered"] = candidate["DOI"] in registered_dois
            candidates.append(candidate)
    candidates.sort(
        key=lambda row: (
            str(row["target_property"]),
            -int(row["pure_target_data_points"]),
            str(row["DOI"]),
        )
    )
    write_candidates_csv(candidates, args.output)
    print(f"Wrote {len(candidates)} candidates to {args.output}.")


if __name__ == "__main__":
    main()
