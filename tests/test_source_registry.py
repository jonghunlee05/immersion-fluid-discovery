import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from immersion_ml.data.download import sha256_file, verify_registered_sources


class SourceRegistryTests(unittest.TestCase):
    def test_registered_thermoml_files_match_sha256(self):
        registry_path = Path("references/thermoml_source_registry.csv")
        with registry_path.open(newline="", encoding="utf-8") as handle:
            sources = list(csv.DictReader(handle))

        self.assertGreaterEqual(len(sources), 4)
        for source in sources:
            with self.subTest(filename=source["filename"]):
                raw_path = Path("data/raw/thermoml") / source["filename"]
                self.assertTrue(raw_path.is_file())
                self.assertEqual(sha256_file(raw_path), source["sha256"])
                self.assertTrue(source["DOI"])
                self.assertTrue(source["source_url"].startswith("https://trc.nist.gov/"))

        self.assertEqual(
            verify_registered_sources(sources, Path("data/raw/thermoml")), []
        )

    def test_verification_reports_missing_and_changed_files(self):
        with TemporaryDirectory() as temp_dir:
            raw_dir = Path(temp_dir)
            source_path = raw_dir / "source.xml"
            source_path.write_text("original", encoding="utf-8")
            source = {
                "filename": source_path.name,
                "sha256": sha256_file(source_path),
            }

            self.assertEqual(verify_registered_sources([source], raw_dir), [])
            source_path.write_text("changed", encoding="utf-8")
            self.assertEqual(
                verify_registered_sources([source], raw_dir),
                [f"checksum_mismatch: {source_path}"],
            )
            source_path.unlink()
            self.assertEqual(
                verify_registered_sources([source], raw_dir),
                [f"missing: {source_path}"],
            )


if __name__ == "__main__":
    unittest.main()
