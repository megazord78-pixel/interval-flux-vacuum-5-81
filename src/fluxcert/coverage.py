"""Exact set-accounting checker for a generated GKZ degree partition."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .verify import VerificationError, _require


REQUIRED_CATEGORIES = (
    "chow_zero",
    "source_table",
    "displayed_multicover",
    "uncovered",
)


def canonical_identifier(value: Any) -> str:
    """Return an unambiguous canonical identifier for a degree representation."""

    _require(isinstance(value, dict), "degree identifier must be an object")
    coefficients = value.get("transverse_coefficients")
    shift = value.get("zero_shift")
    _require(
        isinstance(coefficients, list)
        and len(coefficients) == 5
        and all(isinstance(item, int) and item >= 0 for item in coefficients),
        "degree identifier needs five nonnegative integer coefficients",
    )
    _require(isinstance(shift, int) and shift >= 0,
             "degree identifier needs a nonnegative integer zero shift")
    return ",".join(str(item) for item in coefficients) + f"|{shift}"


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def verify_finite_source_registry(payload: dict[str, Any]) -> dict[str, Any]:
    """Check exact row alignment and the mutation-sensitive canonical digest."""

    rows = payload["rows"]
    _require(payload["row_count"] == 557 and len(rows) == 557,
             "finite source registry must contain exactly 557 rows")
    charges: set[tuple[int, ...]] = set()
    coefficient_count = 0
    for expected_row, row in enumerate(rows, start=1):
        _require(row["source_row_one_based"] == expected_row,
                 "finite source rows are missing, duplicated, or reordered")
        charge = row["full_charge"]
        _require(isinstance(charge, list) and len(charge) == 10
                 and all(isinstance(value, int) for value in charge),
                 f"source row {expected_row} has an invalid full charge")
        charge_tuple = tuple(charge)
        _require(charge_tuple not in charges,
                 f"source registry duplicates charge at row {expected_row}")
        charges.add(charge_tuple)
        _require(isinstance(row["genus_zero_gv"], int),
                 f"source row {expected_row} has a nonintegral GV invariant")
        for term in row["exact_chow_polynomial"]:
            monomial = term["monomial"]
            coefficient = term["coefficient"]
            _require(isinstance(monomial, list) and len(monomial) == 5
                     and all(isinstance(value, int) and value >= 0 for value in monomial),
                     f"source row {expected_row} has an invalid Chow monomial")
            _require(set(coefficient) == {"numerator", "denominator"}
                     and isinstance(coefficient["numerator"], int)
                     and isinstance(coefficient["denominator"], int)
                     and coefficient["denominator"] > 0,
                     f"source row {expected_row} has an invalid rational coefficient")
            coefficient_count += 1
    _require(payload["unique_full_charge_count"] == len(charges) == 557,
             "finite source charges are not unique")
    observed = _canonical_sha256(rows)
    _require(observed == payload["registry_sha256"],
             "finite source registry canonical digest mismatch")
    return {
        "verified": True,
        "row_count": len(rows),
        "exact_rational_coefficient_count": coefficient_count,
        "registry_sha256": observed,
    }


def verify_partition(payload: dict[str, Any]) -> dict[str, Any]:
    """Prove disjointness and exhaustion from explicit membership lists."""

    universe = [canonical_identifier(item) for item in payload["universe"]]
    _require(len(universe) == len(set(universe)), "universe contains duplicates")
    categories = payload["categories"]
    _require(tuple(categories) == REQUIRED_CATEGORIES,
             "coverage categories or their canonical order are wrong")
    seen: set[str] = set()
    counts: dict[str, int] = {}
    for name in REQUIRED_CATEGORIES:
        members = [canonical_identifier(item) for item in categories[name]]
        _require(len(members) == len(set(members)), f"{name} contains duplicates")
        overlap = seen.intersection(members)
        if overlap:
            raise VerificationError(f"degree categories overlap at {min(overlap)}")
        seen.update(members)
        counts[name] = len(members)
    universe_set = set(universe)
    _require(seen == universe_set,
             f"partition mismatch: missing={len(universe_set-seen)}, extra={len(seen-universe_set)}")
    if "zero_generator" in payload or "transverse_generators" in payload:
        zero = payload["zero_generator"]
        transverse = payload["transverse_generators"]
        _require(len(zero) == 10 and len(transverse) == 5
                 and all(len(generator) == 10 for generator in transverse),
                 "partition generators have the wrong dimensions")
        for name in REQUIRED_CATEGORIES:
            for item in categories[name]:
                coefficients = item["transverse_coefficients"]
                shift = item["zero_shift"]
                expected_charge = [
                    sum(coefficients[index] * transverse[index][component]
                        for index in range(5)) + shift * zero[component]
                    for component in range(10)
                ]
                _require(item.get("full_charge") == expected_charge,
                         f"{name} has a coefficient/charge mismatch at {canonical_identifier(item)}")
                chow_nonzero = item.get("chow_nonzero")
                source_row = item.get("source_row_one_based")
                tower = item.get("displayed_baseline_tower_matches")
                expected_category = (
                    "chow_zero" if chow_nonzero is False else
                    "source_table" if source_row is not None else
                    "displayed_multicover" if tower else
                    "uncovered"
                )
                _require(name == expected_category,
                         f"category witness mismatch at {canonical_identifier(item)}")
    canonical_categories = {name: categories[name] for name in REQUIRED_CATEGORIES}
    full_digest = _canonical_sha256(canonical_categories)
    if "partition_sha256" in payload:
        _require(payload["partition_sha256"] == full_digest,
                 "degree partition canonical digest mismatch")
    identifier_digest = hashlib.sha256(json.dumps(
        {name: sorted(canonical_identifier(item) for item in categories[name])
         for name in REQUIRED_CATEGORIES},
        separators=(",", ":"), sort_keys=True,
    ).encode("ascii")).hexdigest()
    return {
        "verified": True,
        "universe_count": len(universe),
        "category_counts": counts,
        "partition_sha256": full_digest,
        "identifier_partition_sha256": identifier_digest,
    }
