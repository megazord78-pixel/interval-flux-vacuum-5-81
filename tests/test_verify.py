import copy
import json
from pathlib import Path
import unittest

from fluxcert import (
    VerificationError,
    audit_certificate,
    verify_certificate,
    verify_tail_propagation,
    verify_tail_source_binding,
)


ROOT = Path(__file__).resolve().parents[1]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads(
            (ROOT / "data" / "certificate.json").read_text(encoding="utf-8")
        )
        cls.finite_witness = json.loads(
            (ROOT / "data" / "full_finite_krawczyk.json").read_text(encoding="utf-8")
        )
        cls.propagation = json.loads(
            (ROOT / "data" / "recentered_tail_propagation.json").read_text(
                encoding="utf-8"
            )
        )
        inputs = cls.propagation["inputs"]
        cls.tail_source = {
            "refined_flux_tail": {
                "tail_propagation": {
                    "tau_fterm_component_tail_upper":
                        inputs["delta_f_component_upper"][0],
                    "complex_structure_fterm_component_tail_upper":
                        inputs["delta_f_component_upper"][1],
                    "tau_real_jacobian_row_sum_tail_upper":
                        inputs["delta_j_row_sum_upper"][0],
                    "complex_structure_real_jacobian_row_sum_tail_upper":
                        inputs["delta_j_row_sum_upper"][1],
                },
                "krawczyk_persistence": {
                    "existing_box_radius": inputs["box_radius"],
                },
            }
        }

    def test_reference_certificate_is_publication_ready(self):
        result = audit_certificate(self.certificate)
        self.assertTrue(result["verified"])
        self.assertEqual(result["strict_components"], 12)
        self.assertFalse(result["physical_vacuum_claim"])
        self.assertEqual(result["publication_blockers"], [])

    def test_reference_certificate_is_admitted(self):
        self.assertTrue(verify_certificate(self.certificate)["verified"])

    def test_schema_rejects_missing_numerical_witness(self):
        damaged = copy.deepcopy(self.certificate)
        del damaged["finite_source_sector"]["box_jet_bounds"]
        with self.assertRaises(VerificationError):
            verify_certificate(damaged)

    def test_rational_pair_bounds_exercise_promotion_path(self):
        finite = self.certificate["finite_source_sector"]
        self.assertIsInstance(finite["box_jet_bounds"]["value_upper"], dict)
        result = verify_certificate(copy.deepcopy(self.certificate))
        self.assertTrue(result["verified"])

    def test_provenance_manifest_is_well_formed(self):
        provenance = self.certificate["provenance"]
        self.assertEqual(len(provenance), 16)
        paths = [item["path"] for item in provenance]
        self.assertEqual(len(paths), len(set(paths)))
        for item in provenance:
            self.assertEqual(len(item["sha256"]), 64)
            int(item["sha256"], 16)

    def test_legacy_tail_radii_are_not_embedded(self):
        tail = self.certificate["all_orders_tail"]
        self.assertNotIn("componentwise_added_radii_upper", tail)
        self.assertNotIn("maximum_componentwise_added_radius_upper", tail)

    def test_recomputes_reference_tail_propagation(self):
        result = verify_tail_propagation(self.finite_witness, self.propagation)
        self.assertEqual(len(result["componentwise_added_radii_upper"]), 12)
        self.assertLessEqual(
            result["preconditioner_infinity_norm_upper"], 2 * 10**23
        )

    def test_tail_vectors_are_bound_to_authenticated_source(self):
        verify_tail_source_binding(self.propagation, self.tail_source)

    def test_rejects_tail_source_vector_mismatch(self):
        damaged = copy.deepcopy(self.tail_source)
        damaged["refined_flux_tail"]["tail_propagation"][
            "tau_fterm_component_tail_upper"
        ] = "1e-76"
        with self.assertRaises(VerificationError):
            verify_tail_source_binding(self.propagation, damaged)

    def test_preconditioner_boolean_is_not_a_proof_input(self):
        damaged_witness = copy.deepcopy(self.finite_witness)
        damaged_witness["preconditioner"][
            "infinity_norm_upper_below_2e23"
        ] = False
        result = verify_tail_propagation(damaged_witness, self.propagation)
        self.assertLessEqual(
            result["preconditioner_infinity_norm_upper"], 2 * 10**23
        )

    def test_rejects_changed_declared_preconditioner_norm(self):
        damaged = copy.deepcopy(self.propagation)
        damaged["preconditioner"]["infinity_norm_upper"]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_tail_propagation(self.finite_witness, damaged)

    def test_rejects_changed_preconditioner_entry(self):
        damaged = copy.deepcopy(self.propagation)
        damaged["preconditioner"]["absolute_entries_upper"][0][0]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_tail_propagation(self.finite_witness, damaged)

    def test_rejects_changed_delta_f_component(self):
        damaged = copy.deepcopy(self.propagation)
        damaged["inputs"]["delta_f_component_upper"][0]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_tail_propagation(self.finite_witness, damaged)

    def test_rejects_changed_delta_j_component(self):
        damaged = copy.deepcopy(self.propagation)
        damaged["inputs"]["delta_j_row_sum_upper"][0]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_tail_propagation(self.finite_witness, damaged)

    def test_rejects_changed_declared_tail_addition(self):
        damaged = copy.deepcopy(self.propagation)
        damaged["componentwise_added_radii_upper"][0]["numerator"] += 1
        with self.assertRaises(VerificationError):
            verify_tail_propagation(self.finite_witness, damaged)

    def test_rejects_global_uniqueness_scope(self):
        damaged = copy.deepcopy(self.certificate)
        damaged["scope"]["local_uniqueness_only"] = False
        with self.assertRaises(VerificationError):
            audit_certificate(damaged)

    def test_rejects_physical_vacuum_promotion(self):
        damaged = copy.deepcopy(self.certificate)
        damaged["scope"]["physical_vacuum"] = True
        with self.assertRaises(VerificationError):
            audit_certificate(damaged)

    def test_rejects_geometry_overclaim(self):
        damaged = copy.deepcopy(self.certificate)
        damaged["supporting_geometry"]["exhausts_all_effective_curves"] = True
        with self.assertRaises(VerificationError):
            audit_certificate(damaged)

    def test_rejects_missing_degree_accounting(self):
        damaged = copy.deepcopy(self.certificate)
        damaged["degree_coverage"]["category_counts"]["source_table"] -= 1
        with self.assertRaises(VerificationError):
            audit_certificate(damaged)


if __name__ == "__main__":
    unittest.main()
