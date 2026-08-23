"""Command-line workflow for the experimental dataset construction stage."""

from __future__ import annotations

import argparse
from pathlib import Path

from immersion_ml.data.audit import coverage_report, overlap_report, write_report_csv
from immersion_ml.data.thermoml import (
    parse_thermoml_directory_with_audit,
    write_raw_measurements_csv,
    write_rejections_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse ThermoML XML files and produce raw audit reports."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing immutable ThermoML XML downloads.",
    )
    parser.add_argument(
        "--interim-csv",
        type=Path,
        default=Path("data/interim/thermoml_raw_measurements.csv"),
        help="Output CSV for parsed one-measurement-per-row records.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports/data_audit"),
        help="Directory for coverage and overlap reports.",
    )
    args = parser.parse_args()

    rows, rejections = parse_thermoml_directory_with_audit(args.raw_dir)
    write_raw_measurements_csv(rows, args.interim_csv)
    write_report_csv(coverage_report(rows), args.report_dir / "coverage_report.csv")
    write_report_csv(overlap_report(rows), args.report_dir / "overlap_report.csv")
    write_rejections_csv(rejections, args.report_dir / "rejection_report.csv")


if __name__ == "__main__":
    main()
