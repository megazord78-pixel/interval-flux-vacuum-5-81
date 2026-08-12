"""Small, dependency-free checker for the published certificate.

This module does not recompute periods or interval Jacobians.  It verifies the
logical last mile from independently generated outward-rounded bounds to the
claimed strict Krawczyk inclusion, checks the declared scientific scope, and
optionally authenticates the upstream artifacts by SHA-256.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


class VerificationError(ValueError):
    """Raised when a certificate is malformed or a strict gate fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, dict):
        _require(set(value) == {"numerator", "denominator"},
                 f"{label} rational pair has the wrong keys")
        numerator = value["numerator"]
        denominator = value["denominator"]
        _require(isinstance(numerator, int) and isinstance(denominator, int)
                 and denominator > 0,
                 f"{label} rational pair is invalid")
        return Decimal(numerator) / Decimal(denominator)
    _require(isinstance(value, str),
             f"{label} must be a decimal string or rational pair")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise VerificationError(f"{label} is not a decimal") from exc
    _require(result.is_finite(), f"{label} must be finite")
    return result


def _fraction(value: Any, label: str) -> Fraction:
    """Parse a published decimal or rational pair without binary floats."""
    if isinstance(value, dict):
        _require(set(value) == {"numerator", "denominator"},
                 f"{label} rational pair has the wrong keys")
        numerator = value["numerator"]
        denominator = value["denominator"]
        _require(isinstance(numerator, int) and isinstance(denominator, int)
                 and denominator > 0,
                 f"{label} rational pair is invalid")
        return Fraction(numerator, denominator)
    _require(isinstance(value, str),
             f"{label} must be a decimal string or rational pair")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise VerificationError(f"{label} is not an exact decimal") from exc


def verify_tail_propagation(
    finite_witness: dict[str, Any], propagation: dict[str, Any]
) -> dict[str, Any]:
    """Recompute every tail contribution from C_new, Delta F, Delta J and r."""
    _require(propagation.get("schema_version") == 1,
             "unsupported tail-propagation schema")
    dimension = finite_witness["preconditioner"]["dimension"]
    _require(dimension == 12, "the recentered preconditioner must be 12 by 12")
    published_matrix = propagation["preconditioner"]["absolute_entries_upper"]
    _require(published_matrix
             == finite_witness["preconditioner"]["absolute_entries_upper"],
             "tail propagation does not use the finite witness C_new matrix")
    matrix = []
    _require(len(published_matrix) == dimension,
             "C_new has the wrong number of rows")
    for i, row in enumerate(published_matrix):
        _require(len(row) == dimension, f"C_new row {i} has the wrong length")
        parsed = [_fraction(value, f"C_new[{i},{j}]")
                  for j, value in enumerate(row)]
        _require(all(value >= 0 for value in parsed),
                 f"C_new row {i} contains a negative absolute bound")
        matrix.append(parsed)

    row_sums = [sum(row, Fraction()) for row in matrix]
    declared_row_sums = [
        _fraction(value, f"C_new row sum[{i}]")
        for i, value in enumerate(
            propagation["preconditioner"]["absolute_row_sums_upper"]
        )
    ]
    _require(declared_row_sums == row_sums,
             "serialized C_new row sums are not exact recomputations")
    infinity_norm = max(row_sums)
    _require(
        _fraction(propagation["preconditioner"]["infinity_norm_upper"],
                  "C_new infinity norm") == infinity_norm,
        "serialized C_new infinity norm is not the recomputed row maximum",
    )
    norm_limit = _fraction(
        propagation["preconditioner"]["required_infinity_norm_limit"],
        "C_new infinity-norm limit",
    )
    _require(norm_limit == Fraction(2 * 10**23),
             "the required C_new norm limit must be exactly 2e23")
    _require(infinity_norm <= norm_limit,
             "the recomputed C_new infinity norm exceeds 2e23")

    inputs = propagation["inputs"]
    delta_f = [_fraction(value, f"DeltaF[{i}]") for i, value in enumerate(
        inputs["delta_f_component_upper"]
    )]
    delta_j = [_fraction(value, f"DeltaJ[{i}]") for i, value in enumerate(
        inputs["delta_j_row_sum_upper"]
    )]
    _require(len(delta_f) == dimension and len(delta_j) == dimension,
             "tail vectors must both have 12 components")
    _require(all(value >= 0 for value in delta_f + delta_j),
             "tail input bounds must be nonnegative")
    radius = _fraction(inputs["box_radius"], "tail box radius")
    _require(radius > 0, "tail box radius must be positive")
    additions = [
        sum(
            matrix[i][j] * (delta_f[j] + radius * delta_j[j])
            for j in range(dimension)
        )
        for i in range(dimension)
    ]
    declared_additions = [
        _fraction(value, f"tail addition[{i}]")
        for i, value in enumerate(propagation["componentwise_added_radii_upper"])
    ]
    _require(declared_additions == additions,
             "componentwise tail additions are not exact recomputations")
    maximum = max(additions)
    _require(
        _fraction(propagation["maximum_componentwise_added_radius_upper"],
                  "maximum tail addition") == maximum,
        "maximum tail addition is not the exact componentwise maximum",
    )
    return {
        "box_radius": radius,
        "componentwise_added_radii_upper": additions,
        "maximum_componentwise_added_radius_upper": maximum,
        "preconditioner_infinity_norm_upper": infinity_norm,
    }


def verify_tail_source_binding(
    propagation: dict[str, Any], tail_artifact: dict[str, Any]
) -> None:
    """Bind the rational propagation vectors to the authenticated tail result."""
    source = tail_artifact["refined_flux_tail"]["tail_propagation"]
    tau_f = _fraction(source["tau_fterm_component_tail_upper"], "source tau DeltaF")
    z_f = _fraction(
        source["complex_structure_fterm_component_tail_upper"],
        "source complex-structure DeltaF",
    )
    tau_j = _fraction(
        source["tau_real_jacobian_row_sum_tail_upper"], "source tau DeltaJ"
    )
    z_j = _fraction(
        source["complex_structure_real_jacobian_row_sum_tail_upper"],
        "source complex-structure DeltaJ",
    )
    expected_f = [tau_f] + [z_f] * 5 + [tau_f] + [z_f] * 5
    expected_j = [tau_j] + [z_j] * 5 + [tau_j] + [z_j] * 5
    inputs = propagation["inputs"]
    observed_f = [
        _fraction(value, f"bound DeltaF[{index}]")
        for index, value in enumerate(inputs["delta_f_component_upper"])
    ]
    observed_j = [
        _fraction(value, f"bound DeltaJ[{index}]")
        for index, value in enumerate(inputs["delta_j_row_sum_upper"])
    ]
    _require(observed_f == expected_f,
             "propagated DeltaF vector disagrees with the tail artifact")
    _require(observed_j == expected_j,
             "propagated DeltaJ vector disagrees with the tail artifact")
    source_radius = _fraction(
        tail_artifact["refined_flux_tail"]["krawczyk_persistence"]
        ["existing_box_radius"],
        "source tail box radius",
    )
    _require(
        _fraction(inputs["box_radius"], "propagation box radius") == source_radius,
        "propagation radius disagrees with the tail artifact",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_provenance(certificate: dict[str, Any], source_root: Path) -> int:
    provenance = certificate["provenance"]
    paths = [item["path"] for item in provenance]
    _require(len(paths) == len(set(paths)), "provenance paths must be unique")
    declared_hashes = {item["path"]: item["sha256"] for item in provenance}
    checked = 0
    for item in provenance:
        path = source_root / item["path"]
        _require(path.is_file(), f"missing provenance artifact: {path}")
        observed = _sha256(path)
        _require(observed == item["sha256"], f"SHA-256 mismatch: {path}")
        checked += 1

    propagation_hash = certificate["all_orders_tail"]["propagation_attachment"][
        "sha256"
    ]
    propagation_items = [
        item for item in provenance if item["sha256"] == propagation_hash
    ]
    _require(len(propagation_items) == 1,
             "tail propagation must identify one provenance artifact")
    propagation_path = source_root / propagation_items[0]["path"]
    propagation = json.loads(propagation_path.read_text(encoding="utf-8"))
    inputs = propagation["inputs"]
    for prefix in ("preconditioner", "tail"):
        artifact_path = inputs[f"{prefix}_artifact"]
        artifact_hash = inputs[f"{prefix}_artifact_sha256"]
        _require(declared_hashes.get(artifact_path) == artifact_hash,
                 f"{prefix} artifact is not pinned to provenance")
    tail_path = source_root / inputs["tail_artifact"]
    tail_artifact = json.loads(tail_path.read_text(encoding="utf-8"))
    verify_tail_source_binding(propagation, tail_artifact)
    return checked


def _verify_geometry(certificate: dict[str, Any]) -> None:
    geometry = certificate["supporting_geometry"]
    curves = geometry["five_rigid_curves"]
    _require(len(curves) == 5, "the supporting table must contain five curves")
    _require(len({tuple(curve["divisor_pair"]) for curve in curves}) == 5,
             "divisor pairs must be distinct")
    _require(len({curve["source_row"] for curve in curves}) == 5,
             "source rows must be distinct")
    for index, curve in enumerate(curves):
        prefix = f"curve[{index}]"
        _require(curve["match_count_among_divisor_pairs"] == 1,
                 f"{prefix}: divisor-pair match is not unique")
        _require(curve["primitive_multiplicity"] == 1,
                 f"{prefix}: class is not primitive")
        _require(curve["face_genus"] == 0, f"{prefix}: face genus is not zero")
        _require(curve["normal_bundle_degrees"] == [-1, -1],
                 f"{prefix}: normal bundle is not O(-1)+O(-1)")
        _require(curve["primitive_binomial_restriction"] is True,
                 f"{prefix}: restriction is not a primitive binomial")
        _require(curve["persists_in_all_orders_log_box"] is True,
                 f"{prefix}: persistence is not certified")
    _require(geometry["exhausts_all_effective_curves"] is False,
             "supporting curves must not be promoted to exhaustive geometry")
    _require(geometry["mixed_gv_vanishing_all_orders"] is False,
             "finite GV evidence must not be promoted to an all-orders theorem")


def audit_certificate(
    certificate: dict[str, Any], source_root: Path | None = None
) -> dict[str, Any]:
    """Audit all supplied bounds, including explicit publication blockers."""

    _require(certificate.get("schema_version") == 1, "unsupported schema")
    scope = certificate["scope"]
    _require(scope["real_dimension"] == 12, "expected a 12-real-dimensional system")
    _require(scope["complex_fields"] == 6, "expected six complex fields")
    _require(scope["local_uniqueness_only"] is True,
             "certificate must state local, not global, uniqueness")
    _require(scope["full_113_field_root"] is False,
             "certificate must not claim a 113-field root")
    _require(scope["physical_vacuum"] is False,
             "certificate must not claim a complete physical vacuum")

    base = certificate["truncated_krawczyk"]
    tail = certificate["all_orders_tail"]
    with localcontext() as context:
        context.prec = 120
        radius = _decimal(base["box_radius"], "box_radius")
        displacement = _decimal(
            base["maximum_center_displacement_upper"], "center displacement"
        )
        contraction = _decimal(
            base["maximum_remainder_row_sum_upper"], "remainder row sum"
        )
        declared_margin = _decimal(
            base["declared_available_margin_lower"], "available margin"
        )
        _require(radius > 0, "box radius must be positive")
        _require(displacement >= 0, "displacement bound must be nonnegative")
        _require(Decimal(0) <= contraction < Decimal(1),
                 "Krawczyk remainder must be a contraction")

        base_image = displacement + contraction * radius
        recomputed_margin = radius - base_image
        _require(recomputed_margin > 0, "truncated Krawczyk image is not strict")
        _require(Decimal(0) < declared_margin <= recomputed_margin,
                 "declared margin is not a conservative lower bound")

        for key in (
            "maximum_fterm_component_upper",
            "real_jacobian_infinity_norm_upper",
            "period_second_log_derivative_upper",
        ):
            _require(_decimal(tail[key], key) >= 0, f"{key} must be nonnegative")

    # These are populated only from an authenticated propagation attachment.
    # Legacy radii in certificate.json are deliberately not proof inputs.
    radii: list[Decimal] = []
    total_images: list[Decimal] = []
    maximum_tail = Decimal(0)
    ratio = Decimal(0)
    preconditioner_norm = Decimal(0)

    _verify_geometry(certificate)
    finite = certificate["finite_source_sector"]
    _require(finite["published_degrees"] == 557,
             "finite source-sector accounting must declare 557 degrees")
    _require(isinstance(finite["pointwise_comparison_only"], bool),
             "finite-sector pointwise status must be boolean")
    blockers = []
    coverage = certificate["degree_coverage"]
    category_sum = sum(coverage["category_counts"].values())
    _require(category_sum == coverage["category_count_sum"],
             "degree-coverage category sum is inconsistent")
    _require(category_sum == coverage["representation_count"],
             "degree-coverage categories do not exhaust the declared low-total representations")
    _require(coverage["high_totals_begin_at"] == coverage["low_total_maximum"] + 1,
             "low/high total boundary is not contiguous")
    _require(_decimal(coverage["high_total_action_lower"], "high-total action") > 0,
             "high-total action lower bound must be positive")
    if coverage["explicit_disjoint_membership_lists_attached"] is not True:
        blockers.append("missing explicit disjoint membership lists for the four low-total degree categories")
    else:
        from .coverage import verify_finite_source_registry, verify_partition
        if "partition" in coverage:
            attachment = {"degree_coverage": {"partition": coverage["partition"]}}
        else:
            descriptor = coverage.get("partition_attachment")
            _require(isinstance(descriptor, dict),
                     "explicit degree coverage requires an embedded or attached partition")
            attachment_path = Path(__file__).resolve().parents[2] / descriptor["path"]
            _require(attachment_path.is_file(), "degree partition attachment is missing")
            _require(_sha256(attachment_path) == descriptor["sha256"],
                     "degree partition attachment SHA-256 mismatch")
            try:
                attachment = json.loads(attachment_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise VerificationError("degree partition attachment is invalid JSON") from exc
        partition_payload = attachment["degree_coverage"]["partition"]
        partition_result = verify_partition(partition_payload)
        _require(partition_result["universe_count"] == coverage["representation_count"],
                 "partition universe count disagrees with the coverage ledger")
        _require(partition_result["category_counts"] == coverage["category_counts"],
                 "partition category counts disagree with the coverage ledger")
        _require(partition_result["partition_sha256"] == coverage["partition_sha256"],
                 "partition digest disagrees with the certificate")
        registry_result = verify_finite_source_registry(
            attachment["finite_source_registry"]
        )
        _require(registry_result["row_count"] == finite["published_degrees"],
                 "finite registry row count disagrees with the certificate")
        _require(registry_result["registry_sha256"] == finite["registry_sha256"],
                 "finite registry digest disagrees with the certificate")
    finite_box_ready = finite["rigorous_box_jet_bound_attached"] is True
    finite_root_ready = finite["recentered_full_finite_sector_root_interval_certified"] is True
    if not finite_box_ready:
        _require(finite["pointwise_comparison_only"] is True,
                 "an uncertified finite sector must be labelled pointwise-only")
        blockers.append("missing rigorous box-wide value/gradient/Hessian bound for the finite 557-degree sector relative to the four-term baseline")
    else:
        _require(finite["pointwise_comparison_only"] is False,
                 "a rigorous finite-sector box bound cannot remain pointwise-only")
        _require("box_jet_bounds" in finite,
                 "finite-sector readiness requires serialized box jet bounds")
        for key in ("value_upper", "gradient_infinity_upper", "hessian_infinity_upper"):
            _require(_decimal(finite["box_jet_bounds"][key], f"finite {key}") >= 0,
                     f"finite {key} must be nonnegative")
    if not finite_root_ready:
        blockers.append("missing interval certificate for a root recentered with the complete finite source sector")
    else:
        _require(finite_box_ready,
                 "a recentered finite-sector root requires the rigorous box jet bound")
        _require("recentered_krawczyk" in finite,
                 "finite-sector root readiness requires a recentered Krawczyk witness")

    if finite_box_ready and finite_root_ready:
        witness_descriptor = finite.get("finite_krawczyk_attachment")
        _require(isinstance(witness_descriptor, dict),
                 "the finite Krawczyk attachment descriptor is missing")
        witness_path = Path(__file__).resolve().parents[2] / witness_descriptor["path"]
        _require(witness_path.is_file(), "the finite Krawczyk attachment is missing")
        _require(_sha256(witness_path) == witness_descriptor["sha256"]
                 == finite["finite_krawczyk_artifact_sha256"],
                 "finite Krawczyk attachment SHA-256 mismatch")
        try:
            finite_witness = json.loads(witness_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VerificationError("finite Krawczyk attachment is invalid JSON") from exc
        witness_conclusions = finite_witness["conclusions"]
        _require(witness_conclusions["rigorous_box_jet_bound_attached"] is True,
                 "finite attachment does not certify its box jets")
        _require(witness_conclusions["recentered_full_finite_sector_root_interval_certified"] is True,
                 "finite attachment does not certify its recentered root")
        _require(witness_conclusions["all_557_exact_chow_rows_included"] is True,
                 "finite attachment does not include all 557 rows")
        _require(witness_conclusions["inverse_mirror_map_interval_certified"] is True,
                 "finite attachment does not certify the inverse mirror map")
        _require(finite_witness["inverse_mirror_map"]["componentwise_self_map_containment"]
                 == [True] * 5,
                 "inverse mirror-map attachment lacks five componentwise inclusions")
        _require(finite_witness["krawczyk"]["componentwise_strict_interior_containment"]
                 == [True] * scope["real_dimension"],
                 "finite attachment lacks twelve componentwise Krawczyk inclusions")
        propagation_descriptor = tail.get("propagation_attachment")
        _require(isinstance(propagation_descriptor, dict),
                 "the recentered tail-propagation attachment is missing")
        propagation_path = (
            Path(__file__).resolve().parents[2] / propagation_descriptor["path"]
        )
        _require(propagation_path.is_file(),
                 "the recentered tail-propagation attachment is missing")
        _require(_sha256(propagation_path) == propagation_descriptor["sha256"],
                 "tail-propagation attachment SHA-256 mismatch")
        try:
            propagation = json.loads(propagation_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VerificationError(
                "tail-propagation attachment is invalid JSON"
            ) from exc
        _require(
            propagation["inputs"]["preconditioner_artifact_sha256"]
            == witness_descriptor["sha256"],
            "tail propagation is not pinned to the attached finite witness",
        )
        propagation_result = verify_tail_propagation(finite_witness, propagation)
        _require(finite_witness["finite_box_jet_bounds"]["value_upper"]
                 == finite["box_jet_bounds"]["value_upper"],
                 "finite value bound disagrees with attachment")
        _require(finite_witness["finite_box_jet_bounds"]["gradient_infinity_upper"]
                 == finite["box_jet_bounds"]["gradient_infinity_upper"],
                 "finite gradient bound disagrees with attachment")
        _require(finite_witness["finite_box_jet_bounds"]["hessian_infinity_upper"]
                 == finite["box_jet_bounds"]["hessian_infinity_upper"],
                 "finite Hessian bound disagrees with attachment")
        recentered = finite["recentered_krawczyk"]
        witness_krawczyk = finite_witness["krawczyk"]
        for key in (
            "box_radius",
            "maximum_center_displacement_upper",
            "maximum_remainder_row_sum_upper",
            "declared_available_margin_lower",
        ):
            _require(recentered[key] == witness_krawczyk[key],
                     f"recentered {key} disagrees with finite attachment")
        with localcontext() as context:
            context.prec = 120
            radius = _decimal(recentered["box_radius"], "recentered box radius")
            displacement = _decimal(
                recentered["maximum_center_displacement_upper"],
                "recentered center displacement",
            )
            contraction = _decimal(
                recentered["maximum_remainder_row_sum_upper"],
                "recentered remainder row sum",
            )
            _require(radius > 0 and displacement >= 0,
                     "recentered radius/displacement are invalid")
            _require(Decimal(0) <= contraction < Decimal(1),
                     "recentered Krawczyk remainder must be a contraction")
            base_image = displacement + contraction * radius
            recomputed_margin = radius - base_image
            _require(recomputed_margin > 0,
                     "recentered finite-sector Krawczyk image is not strict")
            declared_margin = _decimal(
                recentered["declared_available_margin_lower"],
                "recentered available margin",
            )
            _require(Decimal(0) < declared_margin <= recomputed_margin,
                     "recentered declared margin is not conservative")
            _require(
                propagation_result["box_radius"]
                == _fraction(recentered["box_radius"], "recentered box radius"),
                "tail propagation radius disagrees with the recentered box",
            )
            radii = [
                Decimal(value.numerator) / Decimal(value.denominator)
                for value in propagation_result["componentwise_added_radii_upper"]
            ]
            maximum_fraction = propagation_result[
                "maximum_componentwise_added_radius_upper"
            ]
            maximum_tail = (
                Decimal(maximum_fraction.numerator)
                / Decimal(maximum_fraction.denominator)
            )
            norm_fraction = propagation_result[
                "preconditioner_infinity_norm_upper"
            ]
            preconditioner_norm = (
                Decimal(norm_fraction.numerator) / Decimal(norm_fraction.denominator)
            )
            total_images = [base_image + value for value in radii]
            _require(all(value < radius for value in total_images),
                     "all-orders tail does not preserve the recentered box")
            ratio = maximum_tail / declared_margin
        _require(finite.get("infinite_tail_domain_contains_recentered_box") is True,
                 "the infinite-tail domain is not attached to the recentered box")
        shift = _decimal(
            finite["maximum_old_to_new_center_shift_upper"],
            "old-to-new center shift",
        )
        log_domain = _decimal(
            finite["infinite_tail_log_domain_radius_lower"],
            "infinite-tail log-domain radius",
        )
        _require(shift >= 0 and log_domain > 0 and Decimal(8) * (shift + radius) < log_domain,
                 "the recentered field box is not contained in the certified log-domain")
    checked = 0 if source_root is None else _verify_provenance(certificate, source_root)
    return {
        "verified": len(blockers) == 0,
        "claim": (
            "existence and local uniqueness in the declared box"
            if not blockers else "candidate certificate; publication theorem not admitted"
        ),
        "real_dimension": scope["real_dimension"],
        "recomputed_base_image_upper": format(base_image, ".18E"),
        "recomputed_margin_lower": format(recomputed_margin, ".18E"),
        "maximum_all_orders_added_radius_upper": format(maximum_tail, ".18E"),
        "recomputed_preconditioner_infinity_norm_upper": format(
            preconditioner_norm, ".18E"
        ),
        "added_radius_over_declared_margin": format(ratio, ".18E"),
        "strict_components": len(total_images),
        "provenance_files_checked": checked,
        "physical_vacuum_claim": False,
        "publication_blockers": blockers,
        "degree_partition_sha256": (
            None if coverage["explicit_disjoint_membership_lists_attached"] is not True
            else partition_result["partition_sha256"]
        ),
    }


def verify_certificate(
    certificate: dict[str, Any], source_root: Path | None = None
) -> dict[str, Any]:
    """Require a complete publication certificate, rejecting candidate gaps."""

    result = audit_certificate(certificate, source_root)
    _require(result["verified"], "; ".join(result["publication_blockers"]))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificate", nargs="?",
        default=str(Path(__file__).resolve().parents[2] / "data" / "certificate.json"),
    )
    parser.add_argument(
        "--source-root", type=Path,
        help="optional root of the parent research snapshot for SHA-256 checks",
    )
    parser.add_argument(
        "--candidate-audit", action="store_true",
        help="report valid partial bounds and blockers instead of requiring publication readiness",
    )
    arguments = parser.parse_args(argv)
    try:
        payload = json.loads(Path(arguments.certificate).read_text(encoding="utf-8"))
        result = (
            audit_certificate(payload, arguments.source_root)
            if arguments.candidate_audit
            else verify_certificate(payload, arguments.source_root)
        )
    except (OSError, json.JSONDecodeError, VerificationError) as exc:
        print(json.dumps({"verified": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["verified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
