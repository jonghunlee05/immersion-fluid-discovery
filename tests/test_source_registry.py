import csv
import hashlib
import unittest
from pathlib import Path


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
                digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
                self.assertEqual(digest, source["sha256"])
                self.assertTrue(source["DOI"])
                self.assertTrue(source["source_url"].startswith("https://trc.nist.gov/"))


if __name__ == "__main__":
    unittest.main()
