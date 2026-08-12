# Focused publication plan

## Gate A — close the finite-sector gap

1. Freeze all 557 source charges and exact Chow polynomials in a canonical,
   sorted artifact.
2. Partition them into the four baseline primitive towers and the finite
   remainder; attach explicit membership lists.
3. Evaluate the full finite sector with Arb on a box large enough to contain
   the shifted solution.
4. Compute rigorous value, gradient and Hessian difference bounds relative to
   the former four-term system.
5. Recenter and certify the resulting twelve-real-dimensional root.  Do not
   require preservation of the old radius-`1e-30` box if the center moves.

Acceptance: `rigorous_box_jet_bound_attached=true` and
`recentered_full_finite_sector_root_interval_certified=true`, supported by raw
interval witnesses rather than declared flags.

## Gate B — prove complete degree accounting

1. Serialize sorted membership lists for `chow_zero`, `source_table`,
   `displayed_multicover`, and `uncovered` through transverse total eight.
2. Verify pairwise disjointness and exact union with the enumerated monoid
   representations.
3. Attach the high-total geometric witness beginning at total nine.
4. Check the zero-action ray proof separately.

Acceptance: deleting, duplicating or moving one charge makes the verifier fail.

## Gate C — harden reproducibility

1. **Completed for the proof chain:** every `float(Fraction)` serialization
   boundary is replaced by numerator/denominator pairs or explicit directed
   rounding.
2. **Completed for the proof chain:** every consumed parent artifact is
   authenticated, and the verifier binds the propagated tail vectors to the
   authenticated tail result.
3. Pin Arb/python-flint, Normaliz and CYTools versions consistently.
4. Run the isolated verifier on Linux and Windows CI.
5. Obtain one independent reproduction of the final inequality.

## Gate D — finish the paper

1. Author metadata and corresponding-author contact are complete.
2. Complete the exact model/basis definitions and insert generated tables.
3. Add a machine-generated theorem table from the admitted certificate.
4. Keep the five rigid curves in one supporting section and state explicitly
   that they do not exhaust the complete-intersection sector.
5. Deposit code/data with a DOI, then submit the manuscript and arXiv source.

## Recommended submission sequence

1. Private technical reading by one interval-arithmetic specialist.
2. Private technical reading by one mirror-symmetry/flux-vacua specialist.
3. Immutable artifact release and DOI.
4. arXiv submission.
5. Journal submission to a mathematical-physics or high-energy theory venue
   that accepts computationally assisted proofs and has no mandatory APC.

No expansion into Pfaffians, uplift or phenomenology is required for this
paper.
