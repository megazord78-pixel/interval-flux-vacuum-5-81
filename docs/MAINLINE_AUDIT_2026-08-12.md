# Mainline audit snapshot — 2026-08-12

This note records only findings that affect the focused certificate paper.

## Adopted from the parent project

- the Arb/Krawczyk finite-system witness;
- the exact-low and high-total uncovered GKZ bounds;
- componentwise propagation through periods, F-terms and the Jacobian;
- five explicit rigid quotient-basis curves;
- the later correction that those five curves do not exhaust the
  complete-intersection sector.

## Publication-impacting discrepancy

The parent `uncovered_degree_tail` calculation classifies all low-total
representations but removes charges present in the 557-row source table before
forming the uncovered remainder.  The final sharp-tail aggregator then uses
the 188 unique uncovered charges plus the high-total majorant.  The separate
557-row calculation compares with the four-term baseline only at one point and
explicitly declines an all-orders derivative claim.

Therefore the focused verifier retains the finite-source-sector gate as
false.  New parent-project results should be imported only if they provide:

1. explicit box-wide interval jets for the finite-sector difference;
2. a recentered interval root for the complete finite system;
3. immutable data and generator hashes;
4. explicit degree-membership lists.

Changes concerning Pfaffians, open fields, uplift, phenomenology or other
candidate quantum-gravity programs are intentionally ignored by this package.
