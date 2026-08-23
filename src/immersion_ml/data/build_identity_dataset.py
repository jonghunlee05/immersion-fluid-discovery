"""Build the RDKit-validated IFD-004 identity dataset and audits."""

from __future__ import annotations

import argparse
from pathlib import Path

from immersion_ml.data.audit import load_measurements_csv
from immersion_ml.data.identity import (
    IDENTITY_ISSUE_COLUMNS,
    IDENTITY_MEASUREMENT_COLUMNS,
    IDENTITY_REPORT_COLUMNS,
    MOLECULE_CATALOG_COLUMNS,
    resolve_measurement_identities,
    write_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve source identities and build an RDKit molecule catalog."
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path("data/interim/thermoml_raw_measurements.csv"),
    )
    parser.add_argument(
        "--resolved-csv",
        type=Path,
        default=Path("data/interim/thermoml_identity_resolved.csv"),
    )
    parser.add_argument(
        "--catalog-csv",
        type=Path,
        default=Path("data/interim/molecule_catalog.csv"),
    )
    parser.add_argument(
        "--report-dir", type=Path, default=Path("reports/data_audit")
    )
    args = parser.parse_args()

    if not args.input_csv.is_file():
        raise SystemExit(
            f"Missing {args.input_csv}; run "
            "`python -m immersion_ml.data.build_dataset` first."
        )

    rows = load_measurements_csv(args.input_csv)
    resolved, catalog, report, issues = resolve_measurement_identities(rows)
    write_csv(resolved, args.resolved_csv, IDENTITY_MEASUREMENT_COLUMNS)
    write_csv(catalog, args.catalog_csv, MOLECULE_CATALOG_COLUMNS)
    write_csv(
        report,
        args.report_dir / "identity_resolution_report.csv",
        IDENTITY_REPORT_COLUMNS,
    )
    write_csv(issues, args.report_dir / "identity_issues.csv", IDENTITY_ISSUE_COLUMNS)
    print(
        f"Resolved {sum(row['identity_status'] == 'resolved' for row in resolved)} "
        f"of {len(resolved)} measurements into {len(catalog)} molecules; "
        f"issues: {len(issues)}."
    )


if __name__ == "__main__":
    main()
