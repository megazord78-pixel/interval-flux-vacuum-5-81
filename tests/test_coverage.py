import copy
import unittest

from fluxcert import VerificationError, verify_partition


def degree(a, shift=0):
    return {"transverse_coefficients": [a, 0, 0, 0, 0], "zero_shift": shift}


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "universe": [degree(0, 1), degree(1), degree(2), degree(3)],
            "categories": {
                "chow_zero": [degree(0, 1)],
                "source_table": [degree(1)],
                "displayed_multicover": [degree(2)],
                "uncovered": [degree(3)],
            },
        }

    def test_exact_partition(self):
        result = verify_partition(self.payload)
        self.assertTrue(result["verified"])
        self.assertEqual(result["universe_count"], 4)

    def test_deleted_member_fails(self):
        damaged = copy.deepcopy(self.payload)
        damaged["categories"]["source_table"] = []
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_duplicate_across_categories_fails(self):
        damaged = copy.deepcopy(self.payload)
        damaged["categories"]["uncovered"].append(degree(1))
        with self.assertRaises(VerificationError):
            verify_partition(damaged)

    def test_extra_member_fails(self):
        damaged = copy.deepcopy(self.payload)
        damaged["categories"]["uncovered"].append(degree(4))
        with self.assertRaises(VerificationError):
            verify_partition(damaged)


if __name__ == "__main__":
    unittest.main()
