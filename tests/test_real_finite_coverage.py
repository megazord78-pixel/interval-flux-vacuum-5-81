import copy
import json
from pathlib import Path
import unittest

from fluxcert import (
    VerificationError,
    verify_finite_source_registry,
    verify_partition,
)


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "results/2026-08-12_string_5_81_gkz_finite_sector_coverage.json"


class RealFiniteCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_real_557_row_registry(self):
        result = verify_finite_source_registry(
            self.payload["finite_source_registry"]
        )
        self.assertTrue(result["verified"])
        self.assertEqual(result["row_count"], 557)

    def test_real_8150_representation_partition(self):
        result = verify_partition(self.payload["degree_coverage"]["partition"])
        self.assertTrue(result["verified"])
        self.assertEqual(result["universe_count"], 8150)
        self.assertEqual(result["category_counts"], {
            "chow_zero": 7150,
            "source_table": 527,
            "displayed_multicover": 21,
            "uncovered": 452,
        })

    def test_deleting_one_real_member_fails(self):
        damaged = copy.deepcopy(self.payload["degree_coverage"]["partition"])
        damaged["categories"]["source_table"].pop()
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_duplicating_one_real_member_fails(self):
        damaged = copy.deepcopy(self.payload["degree_coverage"]["partition"])
        damaged["categories"]["uncovered"].append(
            copy.deepcopy(damaged["categories"]["uncovered"][0])
        )
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_changing_category_fails(self):
        damaged = copy.deepcopy(self.payload["degree_coverage"]["partition"])
        item = damaged["categories"]["source_table"].pop()
        damaged["categories"]["uncovered"].append(item)
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_changing_representation_coefficient_fails(self):
        damaged = copy.deepcopy(self.payload["degree_coverage"]["partition"])
        damaged["categories"]["uncovered"][0]["transverse_coefficients"][0] += 1
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_changing_exact_chow_coefficient_fails(self):
        damaged = copy.deepcopy(self.payload["finite_source_registry"])
        damaged["rows"][0]["exact_chow_polynomial"][0]["coefficient"]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_finite_source_registry(damaged)


if __name__ == "__main__":
    unittest.main()
