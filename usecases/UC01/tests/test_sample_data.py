"""Validate the synthetic CSV shipped with UC01 using only the Python stdlib."""
import csv
import unittest
from pathlib import Path

DATA = Path(__file__).parents[1] / "data" / "sample_loans.csv"
EXPECTED = {
    "loan_id", "product", "principal_vnd", "tenor_months",
    "dpd", "default_flag", "snapshot_date",
}


class SampleDataTests(unittest.TestCase):
    def test_schema_and_rows(self):
        with DATA.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(set(reader.fieldnames or []), EXPECTED)
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 5)
        self.assertEqual(len({row["loan_id"] for row in rows}), len(rows))
        self.assertTrue(all(row["loan_id"].startswith("SYN") for row in rows))

    def test_numeric_ranges(self):
        with DATA.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        for row in rows:
            self.assertGreater(int(row["principal_vnd"]), 0)
            self.assertGreater(int(row["tenor_months"]), 0)
            self.assertGreaterEqual(int(row["dpd"]), 0)
            self.assertIn(int(row["default_flag"]), (0, 1))


if __name__ == "__main__":
    unittest.main()
