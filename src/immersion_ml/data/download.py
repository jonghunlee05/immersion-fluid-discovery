"""Verify or download immutable ThermoML sources registered by the project."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT = "immersion-fluid-discovery/0.1 (ThermoML research audit)"


def load_source_registry(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_registered_sources(
    registry: list[dict[str, str]], raw_dir: str | Path
) -> list[str]:
    """Return human-readable errors for missing or checksum-mismatched sources."""

    source_dir = Path(raw_dir)
    errors: list[str] = []
    for source in registry:
        filename = source.get("filename", "")
        expected_hash = source.get("sha256", "")
        source_path = source_dir / filename
        if not source_path.is_file():
            errors.append(f"missing: {source_path}")
        elif sha256_file(source_path) != expected_hash:
            errors.append(f"checksum_mismatch: {source_path}")
    return errors


def download_missing_sources(
    registry: list[dict[str, str]], raw_dir: str | Path
) -> None:
    """Download missing registered files without overwriting existing raw data."""

    source_dir = Path(raw_dir)
    source_dir.mkdir(parents=True, exist_ok=True)
    for source in registry:
        destination = source_dir / source["filename"]
        if destination.exists():
            continue
        _download_verified(source, destination)


def _download_verified(source: dict[str, str], destination: Path) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".download", dir=destination.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            request = urllib.request.Request(
                source["source_url"], headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
        actual_hash = sha256_file(temporary_path)
        if actual_hash != source["sha256"]:
            raise ValueError(
                f"Checksum mismatch for {source['filename']}: "
                f"expected {source['sha256']}, got {actual_hash}"
            )
        temporary_path.replace(destination)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify registered ThermoML files or download missing files."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("references/thermoml_source_registry.csv"),
    )
    parser.add_argument(
        "--raw-dir", type=Path, default=Path("data/raw/thermoml")
    )
    parser.add_argument(
        "--download-missing",
        action="store_true",
        help="Download registered files that are not already present.",
    )
    args = parser.parse_args()

    registry = load_source_registry(args.registry)
    if args.download_missing:
        download_missing_sources(registry, args.raw_dir)
    errors = verify_registered_sources(registry, args.raw_dir)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Verified {len(registry)} registered ThermoML source files.")


if __name__ == "__main__":
    main()
